import requests
import json
import time
from decimal import Decimal


class RPT_Bot():

    def __init__(self):
        # base telegram api url with
        self.url = 'https://api.telegram.org/bot<insert bot api key info here>/'
        # This is what we use so in our loop we don't spam chat over and over, used for long polling
        self.update_id_number = 1

    def get_updates(self):
        '''
        Gets a full list of api updates to the bot
        :return: data - the json data of the results
        '''
        # Testing long polling
        params = {'timeout': 5, 'offset': self.update_id_number}
        response = requests.get(self.url + 'getUpdates', data=params)
        data = response.json()
        # return the data from the api call
        return data


    def get_last_update(self, data):
        '''
        Takes the results and returns the last result
        :param data: results we need to parse through the get the last result
        :return: last_update - newest update sent to the bot
        '''
        results = data['result']
        last_update = results[len(results) - 1]
        # return the last update sent to the bot
        return last_update

    def get_chat_id(self, last_response):
        '''
        Gets the chat id to respond to
        :param last_response: data to pull chat id out of
        :return: chat_id - the id of the chat
        '''
        # dig through dat data to get the id
        chat_id = last_response['message']['chat']['id']
        # finally return the id
        return chat_id

    def bot_commmand_switcher(self, last_response):
        '''
        Checks to see if this is a bot command
        :param last_response: data we need to check through
        :return:
        '''
        # Just in case they type in things after the command we split and take the beginning
        msg_text_list = last_response['message']['text'].split()
        msg_text = msg_text_list[0]

        # chat_id is used if we have to post something to chat
        chat_id = self.get_chat_id(last_response)

        # Lets compare against the list of commands we support
        if msg_text == '/price':
            self.price_bot_command(chat_id=chat_id)
        else:
            print('i hit the else rule for {msg}'.format(msg=msg_text))


    def price_bot_command(self, chat_id='1234'):
        '''
        Takes the last response and if bot command is price gets price from southxchange
        :param last_response: - json data of last response
        :param chat_id - used to pass to post_to_chat
        :return:
        '''
        southxchange_url = 'https://www.southxchange.com/api/price/RPT/BTC'
        # lets get the price!
        results = requests.get(southxchange_url)
        # If we get a 200 OKAY
        if results.status_code == requests.codes.ok:
            data = json.loads(results.text)
            # Assign results to variables, we have to format to tell python not
            # to convert our decimals to scientific notation up to 8 decimal places
            bid = format(data['Bid'], '.8f')
            ask = format(data['Ask'], '.8f')
            last = format(data['Last'], '.8f')
            volume = format(data['Volume24Hr'], '.8f')
            # Lets try to pretty this up a bit...
            message = 'RPT/BTC Info:\n'
            message = message + 'Bid          : {bid}\n'.format(bid=bid)
            message = message + 'Ask          : {ask}\n'.format(ask=ask)
            message = message + 'Last         : {last}\n'.format(last=last)
            message = message + 'Volume24Hour : {volume}\n'.format(volume=volume)
            # Time to post that data to chat!
            self.post_to_chat(chat_id=chat_id, message=message)
        else:
            print('Something bad happened, got a code {code}'.format(code=results.status_code))

    def post_to_chat(self, chat_id='1234', message='nodicecowboy'):
        '''
        post message passed to chat_id passed
        :param chat_id:
        :param message:
        :return:
        '''
        chat_url = '{baseurl}sendMessage?chat_id={chat_id}&text={message}'.format(
            baseurl=self.url, chat_id=chat_id, message=message
        )
        results = requests.get(chat_url)

    def set_update_id(self, last_response):
        '''
        We can pass an update id number with long polling to offset the list telegram sends us
        :param last_response: we need to get the last update id from this data
        '''
        # get update ID of last response
        update_id = last_response['update_id']
        update_id_new = int(update_id) + 1
        # we pulled the update ID now lets set it
        self.update_id_number = str(update_id_new)

        # Below was used for debugging purposes only
        #print('update id is {id}'.format(id=update_id_new))





# If the program is called directly then we'll run
if __name__ == '__main__':
    # Create an instance of the RPT_Bot class
    rpt = RPT_Bot()
    while True:
        try:
            responses = rpt.get_updates()
            if responses['result']:
                print(json.dumps(responses, indent=1))
            last_response = rpt.get_last_update(responses)
            rpt.set_update_id(last_response)
            print('in loop, last update id is {id}'.format(id=rpt.update_id_number))
            rpt.bot_commmand_switcher(last_response)
        # If something goes down, don't freak just try again in a few seconds
        except IndexError:
            print('Index out of range, so no results in that timeframe')
        time.sleep(5)



