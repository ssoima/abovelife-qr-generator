import json
import segno
import os
import requests
import re
import cairosvg

os.environ['DEFUSEDXML_ALLOW_CDATA_TAGS'] = '1'

CURRENT_ENVIRONMENT = "test"

#Test Environment Variables
STRAPI_API_TOKEN_TEST = "9892de42d7b69bf675a75ccfdb33b9d778e55c98b12590eb621abdfb7537b314f227e751328e4df2e57ead9c50ec66ebc1eb3366fbcc072018ff174d3b62a5c357a3a62059496372666f9b96958122bc345348e210c4e2705e17b320537f83286fcc908e10ae7f816684036cd7f0e219af948d3d06ef36daf8a0d3c5219f79d9"
STRAPI_URL_TEST = "http://127.0.0.1:1337/api"
QRCODE_SUBFOLDER_TEST = "test_qrcodes"

#Production Environment Variables
STRAPI_API_TOKEN_PRODUCTION = "684efd2a79b3edbe60f7190736399bd598b380447c717aacccba218bb35ba1ce052bcf026257ef8f1b3e23de6c6969314ef29352aa8f1adb1a1295162bf28f3e84100f2f1a096c51a2ac9b09b55300a8db6499874611ad89017b059cfd010973b4f3f6bbf27225127142ed2867617fa086415cd3364f77688ac61550175be3d4"
STRAPI_URL_PRODUCTION = "https://strapi.abovelife.net/api"
QRCODE_SUBFOLDER_PRODUCTION = "production_qrcodes"

if CURRENT_ENVIRONMENT == "test":
    STRAPI_API_TOKEN = STRAPI_API_TOKEN_TEST
    STRAPI_URL = STRAPI_URL_TEST
    QRCODE_SUBFOLDER = QRCODE_SUBFOLDER_TEST

else:
    STRAPI_API_TOKEN = STRAPI_API_TOKEN_PRODUCTION
    STRAPI_URL = STRAPI_URL_PRODUCTION
    QRCODE_SUBFOLDER = QRCODE_SUBFOLDER_PRODUCTION

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
        new_qr_code_url = data['data']['attributes']['url']

        return (new_qr_code_id, new_qr_code_url)
    else:
        return None


def create_seller(name=None):
    url = '%s/sellers' % STRAPI_URL
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


def generate_svg_qr(seller_id, qrcode_id, file_path):
    base_url = '%s/qr/' % ABOVE_FRONTEND_URL

    # Create the subfolder if it doesn't exist

    url = base_url + str(qrcode_id)

    qr = segno.make(url, error='m')

    # Save the QR code as a SVG file
    qr.save(file_path, scale=4, kind='svg')
    with open(file_path, "r") as input_file:
        svg_data = input_file.read()

    # Use a regular expression to extract the <svg> tag and its content
    match = re.search(r'<svg\s.*?>(.*?)</svg>', svg_data, re.DOTALL)

    # If a match is found, modify the <svg> tag and its content and store it in a new variable
    if match:
        svg_tag = match.group(0)
        svg_content = match.group(1)
        modified_svg = re.sub(r'<svg\s+', f'<svg x="4" y="47" ', svg_tag)

        with open('templates/qr_code_template_v5_no_border.svg', 'r') as templateFile:
            svg_template = templateFile.read()

        qr_in_template = svg_template.replace('<insertqr/>', modified_svg)

        with open(file_path, 'w') as f:
            f.write(qr_in_template)

    print("Created QR code \"%s\" for seller \"%s\"" % (qrcode_id, seller_id))


def generate_png(seller_id, qr_id, svg_file_path, png_file_path, pdf_file_path, eps_file_path):
    #cairosvg.svg2pdf(url=svg_file_path, write_to=pdf_file_path, unsafe=True, dpi=300)
    cairosvg.svg2png(url=svg_file_path, write_to=png_file_path, unsafe=True, dpi=300, scale=25)
    #cairosvg.svg2eps(url=svg_file_path, write_to=eps_file_path, unsafe=True, dpi=300)

    def add_inverted_to_path(file_path):
        parts = file_path.split(".")
        return f"{parts[0]}_inverted.{parts[1]}"

    #cairosvg.svg2pdf(url=svg_file_path, write_to=add_inverted_to_path(pdf_file_path), unsafe=True, negate_colors=True, dpi=300)
    cairosvg.svg2png(url=svg_file_path, write_to=add_inverted_to_path(png_file_path), unsafe=True, negate_colors=True, dpi=300, scale=20)
    #cairosvg.svg2eps(url=svg_file_path, write_to=add_inverted_to_path(eps_file_path), unsafe=True, negate_colors=True, dpi=300)


def create_file_path_with_extension (seller_id, qrcode_id, qrcode_url, extension):
    subfolder = '%s/%s' % (QRCODE_SUBFOLDER, seller_id)

    if not os.path.exists(subfolder):
        os.makedirs(subfolder)
    file_path = f'{subfolder}/qr_{qrcode_id}_{qrcode_url}.{extension}'
    return file_path


def create_above_qr(count, seller_ids=None, seller_name=None):

    if seller_ids is None:
        seller_ids = [create_seller(seller_name)]
    for seller_id in seller_ids:
        for i in range(count):
            (qr_id, qr_url) = create_strapi_qr(seller_id)
            svg_file_path = create_file_path_with_extension(seller_id, qr_id, qr_url, 'svg')
            generate_svg_qr(seller_id, qr_id, svg_file_path)
            png_file_path = create_file_path_with_extension(seller_id, qr_id, qr_url, 'png')
            pdf_file_path = create_file_path_with_extension(seller_id, qr_id, qr_url, 'pdf')
            eps_file_path = create_file_path_with_extension(seller_id, qr_id, qr_url, 'eps')

            generate_png(seller_id, qr_id, svg_file_path, png_file_path, pdf_file_path, eps_file_path)



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    create_above_qr(count=5, seller_name="TestWith UUID")
    # print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
#paechter@gmail.com