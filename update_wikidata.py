__author__ = 'Sarah Keating'

from wikidataintegrator import wdi_login
import sys
import reactome_bot
import global_variables
import format_reactome_data


def check_settings(uname, filename):
    """
    Function just to double check we want to write data to wikidata
    :param uname: the username supplied
    :param filename: the filename of reactome data
    :return: True/False depending on whether to proceed
    """
    print('Using input file: {0}'.format(filename))
    if uname == 'SarahKeating':
        print('Using skeating account')
    else:
        print('Using bot account')
    writewd = True
    writing_to_wd = 'N'  # input('write to wikidata (Y)')
    if writing_to_wd == 'Y':
        var = input('Proceed (Y):')
    else:
        writewd = False
        var = 'Y'
    if var == 'Y':
        return [True, writewd]
    else:
        return [False, writewd]


def main(args):
    """Usage: update_wikidata  WDusername, WDpassword (input-filename)
       This program take the input-filename or use data/reactome_data-test.csv
       if none given and write the wikidata pages
    """
    filename = 'data/reactome_data-test.csv'
    if len(args) < 3 or len(args) > 4:
        print(main.__doc__)
        sys.exit()
    elif len(args) == 4:
        filename = args[3]

    [go, writewd] = check_settings(args[1], filename)
    if go:
        bot = reactome_bot.ReactomeBot(writewd)
        server = global_variables.server
        try:
            logincreds = wdi_login.WDLogin(user=args[1], pwd=args[2], server=server)
        except Exception as e:
            print('Error logging into wikidata: {0}'.format(e.args[0]))
            sys.exit()
        data = format_reactome_data.ReactomeData('HSA', 'pathway')
        results = data.get_data_from_reactome(filename)
        if not results:
            print('No wikidata entries made')
            sys.exit()
        bot.set_logincreds(logincreds)
        bot.create_or_update_items(results)
        bot.output_report()

        print('Upload successfully completed')

if __name__ == '__main__':
    main(sys.argv)
