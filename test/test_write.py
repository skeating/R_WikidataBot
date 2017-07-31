__author__ = 'Sarah'

from ReactomeBot import get_data_from_reactome, create_or_update_item
import sys
import os

# reads file and returns it as string
def read_file(path):
    filein = open(path, 'r')
    contents = filein.read()
    filein.close()
    return contents

# do a string comparison of the contents of two file
def compare_files(infile, outfile, fails, not_tested):
    ret = 0
    if not os.path.isfile(infile):
        # we have not added a file to compare to
        not_tested.append(infile)
        print('{0}=================>> MISSING'.format(infile))
        return ret
    elif not os.path.isfile(outfile):
        print(outfile)
        print('{0}=================>> MISSING'.format(outfile))
        fails.append(infile)
        return 1
    indata = read_file(infile)
    out = read_file(outfile)
    if indata.strip() == out.strip():
        print('{0} .... PASSED'.format(infile))
    else:
        fails.append(infile)
        print('{0}=================>> FAILED'.format(infile))
        ret = 1
    return ret




def main(args):
    filename='test_reactome_data.csv'
    results = get_data_from_reactome(filename)
    prep = dict()
    fail = 0
    index = 0
    for result in  results["results"]["bindings"]:
        index = index + 1
        testfile = 'output_test_item{0}.json'.format(index)
        prep = dict()
        written = create_or_update_item(None, result, 1, prep)
        if written:
            fail += compare_files(testfile, 'output_test.json', [], [])
        else:
            print('Failed to write {0}'.format(result['pwLabel']['value']))
            fail += 1
    print('Num fails: {0}'.format(fail))

if __name__ == '__main__':
    main(sys.argv)


