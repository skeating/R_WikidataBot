__author__ = 'Sarah'

from ReactomeBot import get_data_from_reactome
import sys

def fail_unless_equal(a, b):
    fail = 1
    if a == b:
        fail = 0
    return fail

def fail_unless(a):
    if a:
        return 0
    else:
        return 1


def run_test(testname, results, fail, test):
    test = test+1
    result = do_test(testname, results)
    if result==1:
        print('{0} failed'.format(testname))
        fail = fail+1
    return [fail, test]

def do_test(testname, results):
    result = 0
    if (testname == 'test_length_results'):
        result = fail_unless_equal(len(results), 1)
    elif testname == 'test_result_present':
        result = fail_unless('results' in results)
    elif testname == 'test_bindings_present':
        result = fail_unless('bindings' in results['results'])
    elif testname == 'test_two_results':
        result = fail_unless_equal(len(results['results']['bindings']), 2)
    elif testname == 'test_result_1_id':
        result1 = results['results']['bindings'][0]
        result = fail_unless_equal(result1['pwId']['value'], 'R-HSA-5659996')
    elif testname == 'test_result_1_label':
        result1 = results['results']['bindings'][0]
        result = fail_unless_equal(result1['pwLabel']['value'], 'RPIA deficiency: failed conversion of R5P to RU5P')
    elif testname == 'test_result_1_desc':
        result1 = results['results']['bindings'][0]
        result = fail_unless_equal(result1['pwDescription']['value'], ' An instance of RPIA deficiency: failed conversion of R5P to RU5P in Homo Sapiens')
    elif testname == 'test_result_1_publication':
        result1 = results['results']['bindings'][0]
        result = fail_unless_equal(result1['publication']['value'][0], 'http://identifiers.org/pubmed/18987987')
    elif testname == 'test_result_2_publication':
        result1 = results['results']['bindings'][1]
        result = fail_unless_equal(result1['publication']['value'][0], 'http://identifiers.org/pubmed/10583946')
    elif testname == 'test_result_2_publication2':
        result1 = results['results']['bindings'][1]
        result = fail_unless_equal(result1['publication']['value'][1], 'http://identifiers.org/pubmed/1633791')
    elif testname == 'test_result_1_publication_num':
        result1 = results['results']['bindings'][0]
        result = fail_unless_equal(len(result1['publication']['value']), 1)
    elif testname == 'test_result_2_publication_num':
        result1 = results['results']['bindings'][1]
        result = fail_unless_equal(len(result1['publication']['value']), 2)
    return result


def main(args):
    filename='test_reactome_data.csv'
    results = get_data_from_reactome(filename)
    testnames = ['test_length_results', 'test_result_present', 'test_bindings_present', 'test_two_results',
                 'test_result_1_id', 'test_result_1_label', 'test_result_1_desc', 'test_result_1_publication',
                 'test_result_2_publication', 'test_result_1_publication_num', 'test_result_2_publication2',
                 'test_result_2_publication_num']
    test = 0
    fail = 0
    for onetest in testnames:
        [fail, test] = run_test(onetest, results, fail, test)
    print('Num tests: {0}'.format(test))
    print('Num fails: {0}'.format(fail))

if __name__ == '__main__':
    main(sys.argv)

