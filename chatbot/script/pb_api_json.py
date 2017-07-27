import requests

host_base = "https://"

def create_bot(user_key,app_id,host,botname):
    path = '/bot/' + app_id +'/' + botname
    url = host_base + host + path
    query = {"user_key": user_key}
    response = requests.put(url, params=query)
    if response.ok:
        output = botname + ' has been created!'
    else:
        output = 'Bot creation failed! ' + response.json()['message'] + '.'
    return output

def list_bots(user_key, app_id, host):
    path = '/bot/' + app_id
    url = host_base + host + path
    query = {"user_key": user_key}
    response = requests.get(url, params=query)
    if response.ok:
        result = response.json()
        if result:
            output = []
            for elt in range(len(result)):
                output.append( result[elt]['botname'] )
        else:
            output = [False] # Return a false array if no chatbots
    else: 
        output = '%d %s' % (response.status_code, response.reason)
    return output

def delete_bot(user_key,app_id,host,botname):
    path = '/bot/' + app_id +'/' + botname
    url = host_base + host + path
    query = {"user_key": user_key}
    response = requests.delete(url, params=query)
    if response.ok:
        output = botname + ' has been deleted!'
    else: 
        output = 'No bot named ' + botname + ' was found. '
        output += '%d %s' % (response.status_code, response.reason)
    return output

def upload_file(user_key,app_id,host,botname,filename):
    path = '/bot/' + app_id + '/' + botname + '/'
    filepath = filename
    if '/' in filename:
        filename = filename.split('/')[-1]
    file_kind = filename.split('.')[-1]
    if file_kind == 'pdefaults' or file_kind =='properties':
        path += file_kind
    if file_kind == 'map' or file_kind == 'set' or file_kind == 'substitution':
        path += file_kind + '/' + filename.split('.')[0]
    if file_kind == 'aiml':
        path += 'file/' + filename
    if path == '/bot/' + app_id +'/' + botname + '/':
            output = 'File type must be one of the following: substitution, properties, aiml, map, set, or pdefaults'
            return output
    url = host_base + host + path
    data = open(filepath,'rb').read()
    query = {"user_key": user_key}
    response = requests.put(url, params=query, data=data)
    if response.ok:
        return filename + ' successfully uploaded'
    else:
        return response.reason

def list_files(user_key, app_id, host, botname):
    path = '/bot/' + app_id + '/' + botname
    url = host_base + host + path
    query = {"user_key": user_key}
    response = requests.get(url,params=query)
    if response.ok:
        output = response.json()
    else:
        output = response.reason
    return output

def get_file(user_key, app_id, host, botname, filename):
    path = '/bot/' + app_id + '/' + botname +'/'
    file_kind = filename.split('.')[-1]
    if file_kind == 'pdefaults' or file_kind =='properties':
        path += file_kind
    if file_kind == 'map' or file_kind == 'set' or file_kind == 'substitution':
        path += file_kind + '/' + filename.split('.')[0]
    if file_kind == 'aiml':
        path += 'file/' + filename
    url = host_base + host + path
    query = {"user_key": user_key}
    response = requests.get(url, params=query)
    if response.ok:
        output = response.text
    else:
        output = "There was an error with your request: " + response.json()["message"]
    return output

def download_bot(user_key, app_id, host, botname, download_location=False):
    path = '/bot/' + app_id + '/' + botname 
    url = host_base + host + path
    query = {"user_key": user_key,
             "return": 'zip'}
    response = requests.get(url, params=query)
    if response.ok:
        if download_location:
            ofile_path = download_location + botname +'.zip'
        else:
            ofile_path = botname + '.zip'
        ofile = open(ofile_path,'w')
        ofile.write(response.content)
        output = botname + " was downloaded successfully"
    else:
        output =  "Your download request failed: " + response.reason
    return output

def delete_file(user_key, app_id, host, botname, filename):
        path = '/bot/' + app_id + '/' + botname + '/'
        file_kind = filename.split('.')[-1]
        if file_kind == 'pdefaults' or file_kind =='properties':
            path += file_kind
        if file_kind == 'map' or file_kind == 'set' or file_kind == 'substitution':
            path += file_kind + '/' + filename.split('.')[0]
        if file_kind == 'aiml':
            path += 'file/' + filename
        if path == '/bot/' + app_id +'/' + botname + '/':
            output = 'File type must be one of the following: substitution, properties, aiml, map, set, or pdefaults'
            return output
        url = host_base + host + path
        query = {"user_key": user_key}
        response = requests.delete(url, params=query)
        if response.ok:
            output = filename + ' successfully deleted.'
        else:
            output = "There was an error with your request: " + response.json()["message"]
        return output

def compile_bot(user_key,app_id,host, botname):
    path = '/bot/' + app_id +'/' + botname + '/verify'
    url = host_base + host + path
    query = {"user_key": user_key}
    response = requests.get(url, params=query)
    if response.ok:
        output = botname + ' has been successfully compiled!'
    else:
        result = response.json()
        message = result["message"]
        error = str(result["errors"][0])
        output = message + '\n' + error + '\n'
    return output

def talk(user_key, app_id, host, botname, input_text, session_id=False, recent=False, reset=False, trace=False, clientID=False):
    path = '/talk/' + app_id + '/' + botname
    url = host_base + host + path
    query = {"user_key": user_key,
             "input": input_text
             }
    if recent:
        query['recent'] = recent
    if session_id:
        query['sessionid'] = session_id
    if reset:
        query['reset'] = reset
    if trace:
        query['trace'] = trace
    if clientID:
        query['client_name'] = clientID
    response = requests.post(url, params=query)
    result = response.json()
    status = result['status']
    output = {}
    if status == 'ok':
        output["response"] =  result['responses'][0]
        if reset:
            output["output"] = 'Bot has been reset.'
        if trace:
            trace_text = result['trace']
            trace_string = 'Trace: '
            for elt in trace_text:
                if 'status' in elt.keys():
                    trace_string +='Level: ' + str(elt['level']) 
                    trace_string += ' Sentence to process: ' + ' '.join(elt['input']) + ' '
                    trace_string += 'Matched pattern: ' + str(elt['matched'][0])
                    trace_string += ' from file: ' + elt['filename']
                    trace_string += ' template: ' + elt['template'] + '\n'
            output["trace"] = trace_string
        if 'sessionid'  in result:
            output["sessionid"] = result['sessionid']
    else:
        output["response"] = result['message']
    return output


def debug_bot(user_key, app_id, host, botname, input_text="Hello Chatbot", session_id='', recent=True, reset=False, trace=True,clientID=True):
    path = '/talk/' + app_id + '/' + botname
    url = host_base + host + path
    query = {"user_key": user_key,
             "input": input_text,
             "trace": True
             }
    response = requests.post(url, params=query)
    result = response.json()
    return result