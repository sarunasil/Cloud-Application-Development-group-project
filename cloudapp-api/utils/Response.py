from flask import jsonify

# Class for wrapping a response and making it successful or not
# A response is successful when the task has been completed and necessary changes are done
# This is an HTTP response with application/json type which is either of the following:
# {
#   "success": field
# }
#
# {
#   "failure": field
# }
# fielid is a variable of any type (object, array, string, etc...), holds necessary data
class Response:
    @staticmethod
    def responseSuccess(msg='', value={}):
        res_message = 'Success' if msg == '' else msg

        response = {
            'success': res_message
        }

        # response = {**response, **value}

        return jsonify(response)

    @staticmethod
    def responseFailure(msg):
        res_message = 'Something went wrong! Please, try again' if msg == '' else msg

        response = {
            'failure': res_message
        }

        return jsonify(response)