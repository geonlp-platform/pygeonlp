import json
import sys


def print_response(rv):
    print("code:{}, data:'{}'".format(rv.status_code, rv.data),
          file=sys.stderr)


def call_jsonrpc(client, query):
    """
    Send query and return the response.

    Parameters
    ----------
    client: client fixture
    query: dict
        The query string to POST to the server
        in decoded JSON format.
    Return
    ------
    any
        The JSON decoded value of the response.
    """
    if isinstance(query, dict):
        query = json.dumps(query)

    headers = {"Content-Type": "application/json"}
    rv = client.post('/api', data=query, headers=headers)
    assert rv.status_code == 200
    response_object = json.loads(rv.data)
    return response_object


def validate_jsonrpc(client, query, expected):
    """
    Send query and compare the result with expected.

    Parameters
    ----------
    client: client fixture
    query: dict
        The query string to POST to the server
        in decoded JSON format.
    expected: any
        The value expected as a result.
        The JSON decoded value stored in the 'result'
        field of the response is used.

        When '*' is passed as 'expected', any response will pass.

    Return
    ------
    any
        The JSON decoded value stored in the 'result'
        field of the response.
    """
    response_object = call_jsonrpc(client, query)
    result = response_object['result']
    if expected != '*':
        if result != expected:
            print("result: '{}'".format(result), file=sys.stderr)

        assert result == expected

    return result


def validate_jsonrpc_error(client, query, expected_code):
    """
    Send query and compare the status code with expected_code.

    Parameters
    ----------
    client: client fixture
    query: dict
        The query object to POST to the server
        in decoded JSON format.
    expected_code: int
        The expected status_code.
    """
    if isinstance(query, dict):
        query = json.dumps(query)

    headers = {"Content-Type": "application/json"}
    rv = client.post('/api', data=query, headers=headers)
    assert rv.status_code == expected_code


def write_resreq(request, response):
    """
    Write request and response JSON into files.

    Notes
    -----
    The request JSON will be written to
    'docs/source/json/{request['id']}_req.json', and
    the response to 'docs/source/json/{request['id']}_res.json'.

    Parameters
    ----------
    request: dict
        The request in decoded JSON format.
    response: dict
        The response in decoded JSON format.
    """
    basename = request['id']
    with open("docs/source/json/{}_req.json".format(basename), "w") as f:
        json.dump(request, f, indent=2, ensure_ascii=False)
    with open("docs/source/json/{}_res.json".format(basename), "w") as f:
        json.dump(response, f, indent=2, ensure_ascii=False)
