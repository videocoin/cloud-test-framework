import requests

# Taken from https://stackoverflow.com/questions/20658572/python-requests-print-entire-http-request-raw
def get_raw_request(method, url, body={}):
	req = requests.Request(method, url, data=body)
	prepared = req.prepare()

	def pretty_print_POST(req):
	    """
	    At this point it is completely built and ready
	    to be fired; it is "prepared".

	    However pay attention at the formatting used in 
	    this function because it is programmed to be pretty 
	    printed and may differ from the actual request.
	    """
	    print('{}\n{}\r\n{}\r\n\r\n{}'.format(
	        '-----------START-----------',
	        req.method + ' ' + req.url,
	        '\r\n'.join('{}: {}'.format(k, v) for k, v in req.headers.items()),
	        req.body,
	    ))

	pretty_print_POST(prepared)
