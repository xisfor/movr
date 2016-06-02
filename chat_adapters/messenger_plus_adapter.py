from bs4 import BeautifulSoup

class MessengerPlusAdapter:
    """docstring for MessengerPlusAdapter"""
    def __init__(self):
        # super(MessengerPlusAdapter, self).__init__()
        # self.arg = arg

        # self.lines = []
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

        # Import text
        doc_soup = BeautifulSoup(text, "html.parser")

        sessions = self.__sessions_from_soup(doc_soup)
        data['session_count'] = len(sessions)

        # Add a sequence counter to lines for integrity checking
        seq = 1

        # iterate sessions so we can session tag lines
        for session in sessions:
            for line in self.__chatlines_from_soup(session):

                line_hash = self.__hash_for_line(line)
                line_hash['session'] = session['id'].lstrip('Session_')

                line_hash['seq'] = seq
                seq += 1

                if 'user' in line_hash:
                    users.add(line_hash['user'])

                data['lines'].append(line_hash)
                data['line_count'] += 1

        data['users'] = list(users) # coerce set() back to list() for json

        return data

    # ---

    def __hash_for_line(self, line):
        # <tr>
        #     <th><span class="time">(9:45 PM)</span> Isaac Castro XD:</th>
        #     <td style="font-family:&quot;Microsoft Sans Serif&quot;;font-weight:bold;">hey...</td>
        # </tr>

        time_str = line.th.span.text
        user_str = line.th.text.replace(time_str, '')

        # trim up these values
        user_str = user_str.strip()
        if user_str.endswith(":"): user_str = user_str[:-1]

        time_str = time_str.lstrip('(').rstrip(')')

        line_hash = {
            'time' : time_str,
            'user' : user_str,
            'text' : line.td.text
        }

        if line.get('class') != None:
            line_hash['client_notification'] = 'True'
            # remove the user as we don't get that information
            # del line_hash['user']
        else:
            line_hash['client_notification'] = 'False'

        return line_hash


    def __chatlines_from_soup(self, soup):
        return soup.find_all('tr')

    def __sessions_from_soup(self, soup):
        # <div class="mplsession" id="Session_2010-02-01T14-25-56">
        return soup.find_all('div', class_='mplsession')

