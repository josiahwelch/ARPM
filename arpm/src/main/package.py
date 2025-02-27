#This file contains a class that contains information that a package would contain

class Package:

    def __init__(self, name, version, dependencies=None, wget_address=None):
        
        self.name = name
        self.version = version
        self.wget_address = None

        
        #just in case i want to provide the wget address without dependencies
        if dependencies == None:

            self.dependencies = Packages()

        elif isinstance(dependencies, Packages):

            self.dependencies = dependencies

        elif isinstance(dependencies, str):

            self.wget_address = dependencies

            self.dependencies = Packages()


        if self.wget_address == None:

            if wget_address != None:

                self.wget_address = wget_address

            else:

                self.wget_address = ""
        
    def add_dependency(self, dependency):

        self.dependencies.add(dependency)

    def get_name(self):

        return self.name

    def set_name(self, name):

        self.name = name

    def get_version(self):

        return self.version

    def set_version(self, version):

        self.version = version

    def get_dependency_at(self, index):

        return self.dependencies[index]

    def get_dependency(self, name):

        for pkg in self.dependencies:

            if pkg.get_name() == name:

                return pkg

            return package("", -1)

    def get_dependency_count(self):

        return len(self.dependencies)

    def get_dependencies(self):

        return self.dependencies

    def add_dependencies_parse(self, string_to_parse):

        #to make sure there isn't a messed up dependency from an empty dependency list
        if string_to_parse != "[]":

            string_to_parse = string_to_parse.strip("[]")

            for dependency in string_to_parse.split(':'):

                #this gets the name of the package
                name = ""

                for i, element in enumerate(dependency.split('-'), start=0):

                    if i < len(dependency.split('-')) - 1:

                        name += element

                    if i < len(dependency.split('-')) - 2: #I will have no idea how this will work after i reread this tomorrow morning

                        name += '-'

                self.add_dependency(Package(name, dependency.split('-')[-1]))

    def get_wget_address(self):

        return self.wget_address

    def set_wget_address(self, wget_address):

        self.wget_address = wget_address

class Packages:

    def __init__(self):
        
        self.pkgs = []
        self.index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self.index >= self.length():
            raise StopIteration
        result = self.get(self.index)
        self.index += 1
        return result

    def add(self, pkg):

        if isinstance(pkg, Packages):

            for package in pkg:

                self.pkgs.append(package)

        elif isinstance(pkg, Package):

            self.pkgs.append(pkg)

        else:

            raise TypeError

    def remove(self, pkg):

        self.pkgs.remove(pkg)

    def length(self):

        return len(self.pkgs)

    def get(self, index):

        return self.pkgs[index]

    def retrieve(self, name):

        for i in range(self.length()): 

            if self.get(i).get_name() == name:

                return self.get(i)

        return None

    def contains(self, pkg):

        for package in self.pkgs:

            if package.get_name() == pkg.get_name() and pkg.get_version() == pkg.get_version():

                return True

        return False

    def contains_name_only(self, pkg):
        
        for package in self.pkgs:

            if package.get_name() == pkg.get_name():

                return True

        return False

    def add_packages_parse(self, line):

        line = line.strip("[]")
        print(line)

        if ':' in line:

            for package in line.split(':'):

                self.add(Package(package.split('-')[0], package.split('-')[1]))

    def get_packages_parse(self):

        output_string = '['

        for package in self.pkgs:

            #just so there isnt an extraneous colon
            if package != self.get(0):

                output_string += ':'

            output_string += package.get_name()
            output_string += '-'
            output_string += package.get_version()

        output_string += ']'

        return output_string

