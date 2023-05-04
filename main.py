import json
import segno
import os
import requests
import re

STRAPI_API_TOKEN = "9892de42d7b69bf675a75ccfdb33b9d778e55c98b12590eb621abdfb7537b314f227e751328e4df2e57ead9c50ec66ebc1eb3366fbcc072018ff174d3b62a5c357a3a62059496372666f9b96958122bc345348e210c4e2705e17b320537f83286fcc908e10ae7f816684036cd7f0e219af948d3d06ef36daf8a0d3c5219f79d9"
STRAPI_URL = "http://127.0.0.1:1337/api"
ABOVE_FRONTEND_URL = "https://www.abovelife.net"


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


def create_strapi_qr( seller_id ):
    url = '%s/memoria-qrs' % STRAPI_URL
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % STRAPI_API_TOKEN
    }

    new_qr_code_data = {
        'data': {
            'seller': seller_id
        }
    }

    new_qr_code_response = requests.post(url, headers=headers, data=json.dumps(new_qr_code_data))
    if new_qr_code_response.status_code == 200:
        data = new_qr_code_response.json()
        new_qr_code_id = data['data']['id']
        return new_qr_code_id
    else:
        return None


def create_seller(name=None):
    url = 'http://127.0.0.1:1337/api/sellers'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer %s' % STRAPI_API_TOKEN
    }

    new_seller_data = {
        'data': {
        }
    }
    if name:
        new_seller_data['data'] = {
            'name': name
        }

    new_seller_response = requests.post(url, headers=headers, data=json.dumps(new_seller_data))
    if new_seller_response.status_code == 200:
        data = new_seller_response.json()
        new_seller_id = data['data']['id']
        return new_seller_id
    else:
        return None


def generate_svg_qr(seller_id, qrcode_id):
    base_url = '%s/qr/' % ABOVE_FRONTEND_URL

    # Replace this list with the IDs of your users
    # Define the subfolder name
    subfolder = 'qrcodes/%s' % seller_id

    # Create the subfolder if it doesn't exist
    if not os.path.exists(subfolder):
        os.makedirs(subfolder)

    url = base_url + str(qrcode_id)

    qr = segno.make(url, error='m')

    # Save the QR code as a SVG file
    filename = f'{subfolder}/qr_{qrcode_id}.svg'
    qr.save(filename, scale=4, kind='svg')
    with open(filename, "r") as input_file:
        svg_data = input_file.read()

    # Use a regular expression to extract the <svg> tag and its content
    match = re.search(r'<svg\s.*?>(.*?)</svg>', svg_data, re.DOTALL)

    # If a match is found, modify the <svg> tag and its content and store it in a new variable
    if match:
        svg_tag = match.group(0)
        svg_content = match.group(1)
        modified_svg = re.sub(r'<svg\s+', f'<svg x="4" y="47" ', svg_tag)
        print(modified_svg)

        with open('qr_code_template.svg', 'r') as templateFile:
            svg_template = templateFile.read()

        qr_in_template = svg_template.replace('<insertqr/>', modified_svg)

        with open(filename, 'w') as f:
            f.write(qr_in_template)

    print("Created QR code \"%s\" for seller \"%s\"" % (qrcode_id, seller_id))


def create_above_qr(count, seller_ids=None, seller_name=None):

    if seller_ids is None:
        seller_ids = [create_seller(seller_name)]
    for seller_id in seller_ids:
        for i in range(count):
            qr_id = create_strapi_qr(seller_id)
            generate_svg_qr(seller_id, qr_id)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_above_qr(5, seller_name="marcel")
    # print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
