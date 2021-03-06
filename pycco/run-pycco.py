# Generate AVR annotated code.

# The modified Pycco Python file is here:
# C:\Users\roger\AppData\Local\Programs\Python\Python38\Lib\site-packages\pycco\main.py

import glob, os, shutil, re

PYCCO_DOCS_FOLDER = 'docs'

def create_index_file(template_filename, files):
    template_contents = read_file(template_filename)
    index_list = create_index_list(files)
    template_contents = template_contents.replace('{{directory}}', index_list)
    write_file(f'./{PYCCO_DOCS_FOLDER}/master-index.html', template_contents)

def write_file(filename, contents):
    with open(filename, 'w', encoding="utf-8") as f:
        f.write(contents)

def read_file(filename):
    with open(filename, 'r', encoding="utf-8") as f:
        return f.read()

def delete_folder_contents(folder):
    #  Save template file contents.
    directory_template_contents = read_file(f'./{PYCCO_DOCS_FOLDER}/__index.template.html')

    for root, dirs, files in os.walk(folder):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))
    # Restore template file contents.
    write_file(f'./{PYCCO_DOCS_FOLDER}/__index.template.html', directory_template_contents)            

def create_index_list(files):
    index_list = ''
    anchor_tags = []
    template = '{filename}|<li><a href="{url}">{filename}</a></li>'
    root_name = ''
    for file in files:
        if '\\' in file:
            root_name = ''
        else:            
            root_name = '_ROOT_/'
        filename_to_show = root_name + file.replace('\\', '/').lower()
        tag = template.format(url=file + '.html', filename=filename_to_show)
        anchor_tags.append(tag)
    anchor_tags.sort()

    for anchor_tag in anchor_tags:
        anchor_tag = anchor_tag.replace('_ROOT_/', '')
        index_list += re.sub(r'^.*\|', '', anchor_tag)

    return index_list

def is_ignored_file(filename, ignored_files):
    for ignored_file in ignored_files:
        if ignored_file.lower() in filename.lower():
            print(f'Ignored file = {filename}')
            return True
    return False                             
    
if __name__ == '__main__':  
    if not os.path.isdir(f'../{PYCCO_DOCS_FOLDER}'):    
        os.mkdir(f'../{PYCCO_DOCS_FOLDER}')        
    if not os.path.isfile(f'../{PYCCO_DOCS_FOLDER}/__index.template.html'):
        shutil.copy('index.template.html', f'../{PYCCO_DOCS_FOLDER}/__index.template.html')        

    # This program needs to run in the context of the root directory.
    os.chdir('..')
    
    # places to look for source files
    searches = ('global.asax', 'web.config', '**/*.aspx', '**/*.vr', '**/*.js', '**/*.cs' )
    # searches = ('global.asax', 'web.config', '*.aspx', '**/*.aspx', '*.vr', '**/*.vr', 'app_code/*.vr' )
    # source file ending names to ignore.
    ignored_files = ('\\assemblyinfo.','designer.vr', '\\debug')        

    files = []
    for search in searches:
        files.extend(glob.glob(search, recursive=True)) 

    purged_files = []
    for file in files:
        result = is_ignored_file(file, ignored_files)
        if not result:
            purged_files.append(file)       

    delete_folder_contents(f'./{PYCCO_DOCS_FOLDER}')

    for file in purged_files:
        cmd = f'pycco {file} -d ./{PYCCO_DOCS_FOLDER} -l javascript -p >NUL'

        # Separate file name from extension (the extension keeps the .)
        filename, file_extension = os.path.splitext(file)
        # Assign the pycco output file name. Pycco drops the extension and adds
        # .html extension.
        pycco_file = f'{PYCCO_DOCS_FOLDER}\\{filename}.html'

        # Run pycco command
        os.system(cmd)

        # Rename the pycco ouput file to keep the original extension.
        os.rename(pycco_file, f'{PYCCO_DOCS_FOLDER}\\{filename}{file_extension}.html')
        print(f'Output file = {PYCCO_DOCS_FOLDER}\\{filename}{file_extension}.html')

    create_index_file(template_filename=f'./{PYCCO_DOCS_FOLDER}/__index.template.html', files=purged_files)

    shutil.copy("pycco/pycco.css", f'./{PYCCO_DOCS_FOLDER}/')    
