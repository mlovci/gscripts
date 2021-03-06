import os
import itertools
import shutil
from optparse import OptionParser
from glob import glob
from copy import copy
from collections import defaultdict
import sys

def get_params():
    usage="usage: %prog [options]"
    parser = OptionParser(usage=usage)
    parser.add_option("-i","--input_dir",
                      dest="source",
                      default=None,
                      help="directory with unconcatenated fastq files")

    parser.add_option("-o","--output_dir",
                      dest="dest",
                      default=None,
                      help="The destination directory")

    parser.add_option("-k", "--groupby_keys", 
                      dest="groupby_keys",
                      default="1",
                      help="Comma separated string describing which filename elements to group by, ex. 1,3,4")

    parser.add_option("-e", "--extension", 
                      dest="extension", 
                      default=".fastq.gz",
                      help="filter files to concatenate by a specific extension")

    parser.add_option("-p", "--expected_elem", 
                      dest="expected",
                      default=None,
                      help="the number of expected filename elements after splitting by delimiter")

    parser.add_option("-d", "--delimiter", 
                      dest="delimiter",
                      default="_",
                      help="the delimiter to split filename into elements by")

    (options,args) = parser.parse_args()
    if None in [options.source,options.dest]:
        print "error.  must specify source and destination directories."
        parser.print_help()
        sys.exit(-1)
    return options,args



# we have multiple fastq files per library; we concatenate them to get
# a single pair of fastqs per library

def concatenate_files(source,
                      dest, groupby_keys, extension, expected, delimiter):
    if not os.path.exists(source):
        print "input directory %s does not exist." % (source)
        sys.exit(-1)

    if not os.path.exists(dest):
        os.makedirs(dest)
    
    logfile = file(os.path.join(dest,"concatenation_log.txt"),"wb")
    logfile.write("concatenation log\n")
    
    og_filenames = []
    og_filenames = list(sorted(glob(os.path.join(source,'*'+extension))))
    num_og_files = len(og_filenames)
    logfile.write("Number of fastq files: %s\n" % (num_og_files))

    to_group = []
    filepath_map = defaultdict()
        
    for abs_path in og_filenames:
        # remove directory path string
        filename = os.path.basename(abs_path)
        # strip extension
        filename = filename.replace(extension, '')
        # get file information from filename
        filename_vals = filename.split(delimiter)

        if expected and len(filename_vals) != int(expected):
            logfile.write("unexepcted number of filename elements, skipping "+abs_path)
            logfile.write('\n')
            continue

        # determine tokens unique to sample
        unique = []
        non_unique = []
        
        groupby_indexes = [int(element)-1 for element in groupby_keys.split(',')]

        for element in range(len(filename_vals)):
            if element in groupby_indexes:
                unique.append(filename_vals[element])
            else:
                non_unique.append(filename_vals[element])


        unique = tuple(unique)
        non_unique = tuple(non_unique)

        to_group.append((unique, non_unique))
        filepath_map[(unique, non_unique)] = abs_path

     # use itertools groupby to group to unique tokens, then map back to absolute path
     # of original filename

    num_catted = 0
    for key, group in itertools.groupby(sorted(to_group), lambda x: x[0]):
        destination = os.path.join(dest,'_'.join(key)+extension)
        logfile.write('cat to ' + destination)
        logfile.write('\n')
        logfile.write('the files:')
        logfile.write('\n')
            
        # ensure files are not being overwritten
        if not os.path.exists(destination):
            with open(destination, 'wb') as dest_file:
                for tokens in group:
                    file_to_cat = filepath_map[tokens]
                    logfile.write(file_to_cat)
                    logfile.write('\n')
                    with open(file_to_cat, 'rb') as file_obj:
                        shutil.copyfileobj(file_obj, dest_file)
                    num_catted+=1
            logfile.write('\n')
        else:
            logfile.write(destination + ' already exists, skipping')
            logfile.write('\n')

    logfile.close()
    
if __name__=='__main__':
    options, args = get_params()
    concatenate_files(options.source,
                      options.dest,
                      options.groupby_keys,
                      options.extension,
                      options.expected,
                      options.delimiter)
        




