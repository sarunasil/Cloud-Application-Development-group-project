from flask import jsonify

class Response:
    @staticmethod
    def responseSuccess(msg=''):
        res_message = 'Success' if msg == '' else msg

        response = {
            'success': res_message
        }

        return jsonify(response)

    @staticmethod
    def responseFailure(msg):
        res_message = 'Something went wrong! Please, try again' if msg == '' else msg

        response = {
            'failure': res_message
        }

        return jsonify(response)