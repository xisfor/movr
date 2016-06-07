import csv

class CSVAdapter:
    def __init__(self):
        pass

    # this is the public
    def parse_text(self, text):
        # Data structs
        data = {
            'lines' : [],
            'line_count' : 0,
            'session_count': 0
        }
        users = set([]) # use a set() so we can repeatedly rekey
        moves = set([])

        # We're passing in the text already extracted from an open file, using
        # the csv lib directly wont work. Create an iterable list of lines.
        lines = text.splitlines()

        # FIXME: risky business of blindly splitting on ','
        titles = lines.pop(0).split(',')


        # We now use the cs.reader to parse each line
        lines_data = []
        for row in csv.reader(lines):
            line_data = {}
            for i,v in enumerate(row):
                title = titles[i]
                line_data[title] = v

            lines_data.append(line_data)


        # print lines_data

        # Second pass process for output data
        #   line : seq
        #   date : session
        #   time : time
        #   participant : user
        #   Utterance : text

        # use this to when we change session
        cur_session = ''

        for line_data in lines_data:
            ldata = {
                'moves': []
            }
            if line_data['line'] != '' and line_data['line'].isdigit():
                ldata['seq'] = line_data.pop('line')
                ldata['session'] = line_data.pop('date')
                ldata['time'] = line_data.pop('time')
                ldata['user'] = line_data.pop('participant')
                ldata['text'] = line_data.pop('Utterance')
                ldata['client_notification'] = 'False'

                if cur_session != ldata['session']:
                    cur_session = ldata['session']
                    data['session_count'] += 1

                # everything left un-popped should be a move
                for key in line_data:
                    if key != '':
                        moves.add(key) # add all move keys to global move set
                        if line_data[key] != '':
                            ldata['moves'].append(key)

                data['lines'].append(ldata)

                users.add(ldata['user'])


        print data
        data['users'] = list(users) # coerce set() back to list() for json
        data['moves'] = list(moves) # coerce set() back to list() for json

        return data

