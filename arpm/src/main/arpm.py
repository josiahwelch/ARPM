#This file is the main file in the application
#Josiah Welch, February 15th, 2025

from package import Package
from package import Packages
import sys
import subprocess

#gets information from config file
repo = ""

try:

    config_file = open("/etc/arpm.config")

except FileNotFoundError as e:

    config_file = open("/etc/arpm.config", 'w')
    config_file.write("repo=current")
    config_file.close()


for line in config_file:

    if line.startswith("repo="):

        repo = line[5:-1] #the [5:-1] removes the initial "repo=" part and the final newline character
        

#gets information from manifest
primary_packages = Packages()    #primary packages are directly installed by the user/system
secondary_packages = Packages()  #secondary packages are direct or indirect dependencies
tertiary_packages = Packages()   #tertiary packages are packages that are marked for deletion

try:

    pkg_name = ""
    pkg_version = ""
    pkg_dependencies = Packages()
    is_dependency = False
    
    manifest_file = open("/var/lib/arpm/manifest.DAT")
    for i, line in enumerate(manifest_file, start=0): #this supposedly should allow for i to increment with each line

        #the manifest is organized into three line chunks so the program has to iterate over them
        if i % 3 == 0:

            #adds packages to the package record
            if i != 0:

                if is_dependency == True:

                    secondary_packages.add(Package(pkg_name, pkg_version, pkg_dependencies))

                    is_dependency = False

                else:

                    primary_packages.add(Package(pkg_name, pkg_version, pkg_dependencies))

            if line.startswith("dep$"):

                is_dependency = True
                
                pkg_name = (line.split('\n')[0]).split('$')[1] #this is really ugly...

            else:

                pkg_name = line.split('\n')[0] #I added the .split('\n')[0] to remove anything after the newline


        if (i - 1) % 3 == 0:

            pkg_version = line.split('\n')[0] #I added the .split('\n')[0] to remove anything after the newline


        if (i - 2) % 3 == 0:

            pkg_dependencies.add_packages_parse(line.split('\n')[0]) #I added the .split('\n')[0] to remove anything after the newline

        i += 1

    #adds the final package
    if is_dependency == True:

        secondary_packages.add(Package(pkg_name, pkg_version, pkg_dependencies))

        is_dependency = False

    else:

        primary_packages.add(Package(pkg_name, pkg_version, pkg_dependencies))

    manifest_file.close()
    
except FileNotFoundError as e:

    manifest_file = open("/var/lib/arpm/manifest.DAT", 'w')
    manifest_file.close()


#handles compilation of repo
all_packages = Packages()
wget_addresses = {}

#this handles updating the repos
if ('u' in sys.argv[1] and sys.argv[1][0] == '-') or sys.argv[1] == "--update": #the first conditional pair allows for many flags

    subprocess.call(["rm", "-rf", "/tmp/updating_repo.log"])

    subprocess.call(["touch", "/tmp/updating_repo.log"]) #creates log file

    subprocess.call(["rm", "-rf", "/var/lib/arpm/repos/" + repo + ".arcarepo"])

    subprocess.call(["wget", "--show-progress", "-o", "/tmp/updating_repo.log", "-nc", "https://raw.githubusercontent.com/josiahwelch/arca-files/refs/heads/main/" + repo + ".arcarepo", "-P", "/var/lib/arpm/repos/"])

try:

    repo_file = open("/var/lib/arpm/repos/" + repo + ".arcarepo")

#handles missing repo file
except FileNotFoundError as e: 

        print("Arca repo file not found!")

wget_address = ""
pkg_name = ""
pkg_version = ""

#the following block of code operates similarly to the previous nearly-identical block of code
for i, line in enumerate(repo_file, start=0):

    if i % 3 == 0:
        
        if i != 0:

            all_packages.add(Package(pkg_name, pkg_version, wget_address))

        pkg_name = line.split('\n')[0] #I added the .split('\n')[0] to remove anything after the newline

    if (i - 1) % 3 == 0:

        pkg_version = line.split('\n')[0] #I added the .split('\n')[0] to remove anything after the newline
  

    if (i - 2) % 3 == 0:

        #the program needs to keep track of the web addresses so the package manager can pull the tar file
        wget_address = line.split('\n')[0] #I added the .split('\n')[0] to remove anything after the newline

    i += 1
    
all_packages.add(Package(pkg_name, pkg_version, wget_address)) #adds the final package

repo_file.close()


#checks for package updates

updated_packages = Packages()

if ('u' in sys.argv[1] and sys.argv[1][0] == '-') or sys.argv[1] == "--update": #same conditional from previously

    for package in all_packages:

        #checks if an installed package has a newer version in the repo
        if primary_packages.contains_name_only(package) and not primary_packages.contains(package):

            updated_packages.add(package)

        #checks if a dependency has a newer version in the repo
        if secondary_packages.contains_name_only(package) and not secondary_packages.contains(package):

            updated_packages.add(package)
            
    if updated_packages.length() > 0:

        if updated_packages.length() > 1:

            print(str(updated_packages.length()) + " packages are ready for updates.") 

        else:

            print("1 package is ready for an update.")

    else:
        
        print("All packages are up to date!")


#handles searching for packages
elif ('s' in sys.argv[1] and sys.argv[1][0] == '-') or sys.argv[1] == "--search": #similar conditional from previously

    if len(sys.argv) < 3:

        print("Missing search argument!")

    for package in all_packages:

        #this series of if and elifs are used so the package manager can denote installed dependencies and packages
        if sys.argv[2] in package.get_name():

            if primary_packages.contains(package):

                print(package.get_name() + '-' + package.get_version() + "(installed)")

            elif primary_packages.contains_name_only(package):

                print(package.get_name() + '-' + package.get_version() + "(installed, version " + primary_packages.retrieve(package.get_name()).get_version() + ')')

            elif secondary_packages.contains(package):

                print(package.get_name() + '-' + package.get_version() + "(dependency)")

            elif secondary_packages.contains_name_only(package):

                print(package.get_name() + '-' + package.get_version() + "(dependency, version " + seconary_packages.retrieve(package.get_name()).get_version() + ')')

            else:

                print(package.get_name() + '-' + package.get_version())


#handles package installation
elif ('i' in sys.argv[1] and sys.argv[1][0] == '-') or sys.argv[1] == "--install": #similar conditional from previously

    packages_to_be_installed = Packages() #this becomes important later when the package manager goes to process the arpm files

    dependencies_to_be_installed = Packages() #this also becomes important later

    if len(sys.argv) < 3:

        print("Missing installation argument!")

    for i in range(len(sys.argv) - 2):

        if sys.argv[i + 2].endswith(".arcarepo"):

            pkg_file = open(sys.argv[i + 2]) #I am pretty sure it should be i + 2 since i starts at 0

        elif all_packages.contains_name_only(Package(sys.argv[i + 2], "")):

            subprocess.call(["wget", "--show-progress", "-a", "/tmp/updating_repo.log", "-nc", str(all_packages.retrieve(sys.argv[i + 2]).get_wget_address()), "-P", "/tmp/arpm/"])

            packages_to_be_installed.add(all_packages.retrieve(sys.argv[i + 2]))

    #handles the processing of the arpm file
    for package in packages_to_be_installed:
            
        pkg_build_file = open("/tmp/arpm/pkg_build.sh", 'w')

        pkg_build_file.write("#!/usr/bin/bash\n")

        pkg_file = open("/tmp/arpm/" + package.get_name() + '-' + package.get_version() + ".arpm")

        for i, line in enumerate(pkg_file, start=0):

            if i == 0:
                
                if package.get_name() != line.split('\n')[0]:

                   print("Package installation error: " + package.get_name() + " doesn't match with arpm file metadata")

            if i == 1:

               if package.get_version() != line.split('\n')[0]:

                   print("Package installation error: " + package.get_name() + " doesn't match with arpm file metadata")

            if i == 2:

                package.add_dependencies_parse(line.split('\n')[0])

            if i > 2:

                pkg_build_file.write(line)
                pkg_build_file.write('\n')
            
        primary_packages.add(package)
        
        dependencies_to_be_installed.add(package.get_dependencies())
        
        pkg_build_file.close()

        subprocess.call(["chmod", "+x", "/tmp/arpm/pkg_build.sh"])

        subprocess.call(["bash", "/tmp/arpm/pkg_build.sh"])

        subprocess.call(["rm", "/tmp/arpm/pkg_build.sh"])


    #handles dependency installation
    for package in dependencies_to_be_installed: #this is nearly identical to the previous installation code... I really should've refactored this, but who cares

        try:

            subprocess.call(["wget", "--show-progress", "-a", "/tmp/updating_repo.log", "-nc", str(all_packages.retrieve(package.get_name()).get_wget_address()), "-P", "/tmp/arpm/"])
        
        except AttributeError as e:

            print("Missing wget address for " + package.get_name())

        pkg_build_file = open("/tmp/arpm/pkg_build.sh", 'w')

        pkg_build_file.write("#!/usr/bin/bash\n")

        pkg_file = open("/tmp/arpm/" + package.get_name() + '-' + package.get_version() + ".arpm")

        for i, line in enumerate(pkg_file, start=0):

            if i == 0:
                
                if package.get_name() != line.split('\n')[0]:

                   print("Dependency installation error: " + package.get_name() + " doesn't match with arpm file metadata")

            if i == 1:

               if package.get_version() != line.split('\n')[0]:

                   print("Dependency installation error: " + package.get_name() + " doesn't match with arpm file metadata")

            if i == 2:

                package.add_dependencies_parse(line.split('\n')[0])
           
            if i > 2:

                pkg_build_file.write(line)
                pkg_build_file.write('\n')
            
        secondary_packages.add(package)

        if package.get_dependencies().length() > 0:

            dependencies_to_be_installed.add(package.get_dependencies())
        
        pkg_build_file.close()

        subprocess.call(["chmod", "+x", "/tmp/arpm/pkg_build.sh"])

        subprocess.call(["bash", "/tmp/arpm/pkg_build.sh"])

        subprocess.call(["rm", "/tmp/arpm/pkg_build.sh"])

#handles package deletion... I honestly have no idea how to actually implement this
elif ('r' in sys.argv[1] and sys.argv[1][0] == '-') or sys.argv[1] == "--remove": #similar conditional from previously

    if len(sys.argv) < 3:

        print("Missing installation argument!")

    for i in range(len(sys.argv) - 2):

        #it stops you from trying to remove a dependency that wasn't deliberately installed
        if secondary_packages.contains_name_only(Package(sys.argv[i + 2], "")):

            if primary_packages.contains_name_only(Package(sys.argv[i + 2], "")):

                print("Do you want to demote " + sys.argv[i + 2] + "? (y/n):", end=' ')
                
                if sys.stdin.read(1) == 'y' or sys.stdin.read(1) == '\n':

                    primary_packages.remove(primary_packages.retrieve(sys.argv[i + 2]))

                    print(sys.argv[i + 2] + " has been demoted.")

                else:

                    print("Aborting...")
            else:

                print("ERROR: package " + sys.argv[i + 2] + " is a dependency!")

        elif not primary_packages.contains_name_only(Package(sys.argv[i + 2], "")):

            print("ERROR: package " + sys.argv[i + 2] + " is not installed!")

else:

    print(sys.argv[1] + " is unknown!")


#writes to the manifest file
manifest = open("/var/lib/arpm/manifest.DAT", 'w')

for package in primary_packages:

    manifest.write(package.get_name() + '\n')

    manifest.write(package.get_version() + '\n')

    manifest.write(package.get_dependencies().get_packages_parse() + '\n')

for package in secondary_packages:

    manifest.write("dep$" + package.get_name() + '\n')

    manifest.write(package.get_version() + '\n')

    manifest.write(package.get_dependencies().get_packages_parse() + '\n')

