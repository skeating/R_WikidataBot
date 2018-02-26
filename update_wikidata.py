__author__ = 'Sarah Keating'

from wikidataintegrator import wdi_login
import sys
import reactome_bot
import global_variables
import format_reactome_data


def check_settings(uname):
    """
    Function just to double check we want to write data to wikidata
    :param uname: the username supplied
    :return: True/False depending on whether to proceed
    """
    if uname == 'SarahKeating':
        print('Using skeating account')
    else:
        print('Using bot account')
    writewd = True
    writing_to_wd = input('write to wikidata (Y):')
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
    filename = 'data/entity_data_test.csv'
    if len(args) < 3 or len(args) > 4:
        print(main.__doc__)
        sys.exit()
    elif len(args) == 4:
        filename = args[3]

    [proceed, writewd] = check_settings(args[1])
    if proceed:
        bot = reactome_bot.ReactomeBot(writewd)
        server = global_variables.server
        try:
            logincreds = wdi_login.WDLogin(user=args[1], pwd=args[2], server=server)
        except Exception as e:
            print('Error logging into wikidata: {0}'.format(e.args[0]))
            sys.exit()
        # data = format_reactome_data.ReactomeData('HSA', 'pathway')
        # results = data.get_data_from_reactome(filename)
        # if not results:
        #     print('No wikidata entries made')
        #     sys.exit()
        # bot.set_logincreds(logincreds)
        # bot.create_or_update_items(results, 'pathway')
        # bot.output_report()

        data = format_reactome_data.ReactomeData('HSA', 'entity')
        results = data.get_data_from_reactome(filename)
        if not results:
            print('No wikidata entries made')
            sys.exit()
        bot.set_logincreds(logincreds)
        bot.create_or_update_items(results, 'entity')
        bot.output_report()
        print('Upload successfully completed')

if __name__ == '__main__':
    main(sys.argv)