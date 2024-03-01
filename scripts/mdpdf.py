import markdown2
import pdfkit
import tempfile

import os
from pyhtml2pdf import converter

#path = os.path.abspath('index.html')
#converter.convert(f'file:///{path}', 'sample.pdf')


def main(md_text):

    converter.convert(f'file:///./data/sample_mdpdf.html', 'data/output.pdf')


    #converter.convert('https://pypi.org', 'sample.pdf')


    # # Convert Markdown to HTML
    # html_text = markdown2.markdown(md_text)
    #     # Create a temporary file
    # with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_md_file:
    #     temp_md_path = temp_md_file.name
    #     # Write the markdown content to the temporary file
    #     temp_md_file.write(html_text.encode('utf-8'))

    #     converter.convert(temp_md_path, 'sample.pdf')

#    markdown_to_pdf(md_text, "md_output.pdf")



def markdown_to_pdf(markdown_text, output_filename):
    # Convert Markdown to HTML
    html_text = markdown2.markdown(markdown_text)

    # Convert HTML to PDF
    pdfkit.from_string(html_text, output_filename)

# def markdown_to_pdf(markdown_text, output_pdf_path):
#     # Create a temporary file
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_md_file:
#         temp_md_path = temp_md_file.name
#         # Write the markdown content to the temporary file
#         temp_md_file.write(markdown_text.encode('utf-8'))

#     try:
#         # Use Pandoc to convert the Markdown file to PDF
#         subprocess.run(["pandoc", temp_md_path, "-o", output_pdf_path], check=True)
#     except subprocess.CalledProcessError as e:
#         print("Error in converting Markdown to PDF", e)
#     finally:
#         # Remove the temporary file
#         os.remove(temp_md_path)

# # Example usage
# markdown_content = "# Hello, Pandoc\nThis is a Markdown text."
# markdown_to_pdf(markdown_content, "output.pdf")

if __name__ == "__main__":
    md_text = """
    ![](https://sym-public-assets.s3.us-west-2.amazonaws.com/prompt-flow-assets/46/Screenshot+2023-11-27+at+12.36.02+PM.png)

    **<span style="font-size: 30px;">Overview</span>**
    <span style="font-size: 16px;">This Is the content</span><span style="color: rgb(85,89,92);background-color: rgb(255,255,255);font-size: 16px;font-family: Nunito Sans", -apple-system, "system-ui", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol;">This Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the contentThis Is the content</span>

    <span style="color: rgb(85,89,92);background-color: rgb(255,255,255);font-size: 30px;font-family: Nunito Sans", -apple-system, "system-ui", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol;">Action steps</span>

    - <span style="color: rgb(85,89,92);background-color: rgb(255,255,255);font-size: 16px;font-family: Nunito Sans", -apple-system, "system-ui", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol;">Step1</span>
    - <span style="color: rgb(85,89,92);background-color: rgb(255,255,255);font-size: 16px;font-family: Nunito Sans", -apple-system, "system-ui", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol;">Step 2</span>
    - <span style="color: rgb(85,89,92);background-color: rgb(255,255,255);font-size: 16px;font-family: Nunito Sans", -apple-system, "system-ui", "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif, "Apple Color Emoji", "Segoe UI Emoji", "Segoe UI Symbol;">Step 3</span>

    <span style="color: rgb(0,0,0);background-color: rgb(255,255,255);font-size: 14px;font-family: Open Sans", Arial, sans-serif;">Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum</span>
    """
    main(md_text)