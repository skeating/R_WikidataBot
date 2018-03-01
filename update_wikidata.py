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
    :return: [proceed, writeWD, fast] depending on whether to proceed and what settings to use
    """
    if uname == 'SarahKeating':
        print('Using skeating account')
    else:
        print('Using bot account')
    writewd = True
    fast = True
    writing_to_wd = input('write to wikidata (Y):')
    if writing_to_wd == 'Y':
        fastvar = input('using fastrun (Y):')
        if fastvar != 'Y':
            fast = False
        var = input('Proceed (Y):')
    else:
        writewd = False
        var = 'Y'
    if var == 'Y':
        return [True, writewd, fast]
    else:
        return [False, writewd, fast]

def write_data_from_file(data_type, filename, bot, logincreds):
        data = format_reactome_data.ReactomeData('HSA', data_type)
        results = data.get_data_from_reactome(filename)
        if not results:
            print('No wikidata entries made')
            sys.exit()
        bot.set_logincreds(logincreds)
        # because we are creating cyclic relationships sometimes on the first run an entry is not yet
        # present so we check and do another run
        # put in a count so we dont endlessly cycle
        done = False
        count = 0
        while not done and count < 1:
            bot.create_or_update_items(results, data_type)
            count += 1
            if len(global_variables.used_wd_ids['reactome']) == 0:
                done = True
            elif count < 2:
                global_variables.used_wd_ids['reactome'] = []


def main(args):
    """Usage: update_wikidata  WDusername, WDpassword (input-filename)
       This program take the input-filename or use data/reactome_data-test.csv
       if none given and write the wikidata pages
    """
    test = True
    filename = 'data/modprot_data_test.csv'
    data_type = 'modprot'
#    filename = 'data/entity_data_dup.csv'
#    data_type = 'entity'
    if len(args) < 3 or len(args) > 4:
        print(main.__doc__)
        sys.exit()
    elif len(args) == 4:
        filename = args[3]

    # when testing use
    proceed = True
    writewd = False
    fast = False
    if not test:
        [proceed, writewd, fast] = check_settings(args[1])

    if proceed:
        bot = reactome_bot.ReactomeBot(writewd)
        bot.set_fast_run(fast)
        server = global_variables.server
        try:
            logincreds = wdi_login.WDLogin(user=args[1], pwd=args[2], server=server)
        except Exception as e:
            print('Error logging into wikidata: {0}'.format(e.args[0]))
            sys.exit()

        write_data_from_file(data_type, filename, bot, logincreds)
        bot.output_report()
        print('Upload successfully completed')

if __name__ == '__main__':
    main(sys.argv)
