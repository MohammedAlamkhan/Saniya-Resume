#!/usr/bin/env python3
import os
import argparse
from weasyprint import HTML, CSS
from urllib.parse import urljoin
from bs4 import BeautifulSoup

def find_css_files(soup, base_dir):
    """Find all CSS files referenced in the HTML."""
    css_files = []
    for link in soup.find_all('link'):
        if (link.get('rel', [''])[0].lower() == 'stylesheet' and 
            link.get('href')):
            css_path = link['href']
            if not css_path.startswith(('http://', 'https://')):
                # Convert relative path to absolute path
                abs_path = os.path.join(base_dir, css_path)
                if os.path.exists(abs_path):
                    css_files.append(abs_path)
                else:
                    print(f"Warning: CSS file not found: {abs_path}")
    return css_files

def load_css_files(css_files):
    """Load CSS files and return list of CSS objects."""
    stylesheets = []
    for css_file in css_files:
        try:
            with open(css_file, 'r') as f:
                stylesheets.append(CSS(string=f.read()))
        except Exception as e:
            print(f"Warning: Could not load CSS file {css_file}: {e}")
    
    # Add default page styling
    default_css = CSS(string='''
        @page {
            size: A4;
            margin: 1cm;
            @top-center {
                content: '';
            }
            @bottom-center {
                content: counter(page);
            }
        }
    ''')
    stylesheets.append(default_css)
    return stylesheets

def convert_html_to_pdf(html_path, output_pdf, page_size='A4', margin='1cm', 
                       include_css=True, add_page_numbers=True):
    # Get the absolute directory path of the HTML file
    base_dir = os.path.abspath(os.path.dirname(html_path))
    
    # Read the HTML file
    with open(html_path, 'r') as f:
        html_content = f.read()
    
    # Parse HTML
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Convert all relative image paths to absolute paths
    for img in soup.find_all('img'):
        src = img.get('src')
        if src and not src.startswith(('http://', 'https://', '/')):
            abs_path = os.path.join(base_dir, src)
            img['src'] = 'file://' + abs_path
    
    # Handle CSS files
    stylesheets = []
    if include_css:
        css_files = find_css_files(soup, base_dir)
        stylesheets = load_css_files(css_files)
    
    # Create custom CSS for page setup
    page_css = f'''
        @page {{
            size: {page_size};
            margin: {margin};
            {('@bottom-center { content: counter(page); }' 
              if add_page_numbers else '')}
        }}
    '''
    stylesheets.append(CSS(string=page_css))
    
    # Convert to PDF
    HTML(string=str(soup)).write_pdf(
        output_pdf,
        stylesheets=stylesheets
    )

def main():
    parser = argparse.ArgumentParser(description='Convert HTML file with images to PDF')
    parser.add_argument('html_file', help='Path to the HTML file')
    parser.add_argument('--output', '-o', help='Output PDF file path', 
                       default='output.pdf')
    parser.add_argument('--size', '-s', help='Page size (e.g., A4, Letter)', 
                       default='A4')
    parser.add_argument('--margin', '-m', help='Page margin (e.g., 1cm, 0.5in)', 
                       default='1cm')
    parser.add_argument('--no-css', action='store_true', 
                       help='Ignore external CSS files')
    parser.add_argument('--no-page-numbers', action='store_true', 
                       help='Disable page numbers')
    
    args = parser.parse_args()
    
    try:
        convert_html_to_pdf(
            args.html_file,
            args.output,
            page_size=args.size,
            margin=args.margin,
            include_css=not args.no_css,
            add_page_numbers=not args.no_page_numbers
        )
        print(f"Successfully converted {args.html_file} to {args.output}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    main()