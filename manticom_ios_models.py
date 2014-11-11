# manticom_ios_models
# Copyright (C) 2014, Collin Schupman at Yeti LLC

# This is a script to create the models needed iOS side from a given JSON file

# Assumes JSON is in format : TODO->Write format

# TODO: Clean this shit up, get input from user where to put files

import datetime

MODEL_DATA_TYPES = {
    "date"       : "NSDate",
    "datetime"   : "NSDate",
    "int"        : "NSNumber",
    "integer"    : "NSNumber",
    "integer16"  : "NSNumber",
    "integer32"  : "NSNumber",
    "integer64"  : "NSNumber",
    "decimal"    : "NSNumber",
    "double"     : "NSNumber",
    "real"       : "NSNumber",
    "float"      : "NSNumber",
    "string"     : "NSString",
    "text"       : "NSString",
    "boolean"    : "NSNumber",
    "array"      : "NSArray"
}


def write_models_to_file(objects):
    for obj in objects:
        obj_name = obj.keys()[0]
        with open(obj_name[1:] + ".h", "w") as f:

            f.write('//\n')
            f.write('// ' + obj_name[1:] + ".h\n")
            f.write('//\n')
            f.write('// Created by Manticom on ' + str( datetime.datetime.now() ) +'\n')
            f.write('// Copyright (c) ' + str(datetime.datetime.now().year) + ' Manticom. All rights reserved.\n')
            f.write('\n')

            f.write('#import <Foundation/Foundation.h>\n')
            f.write('#import <CoreData/CoreData.h>\n\n')

            custom_classes = set([])
            obj_fields = obj[obj_name]

            for key, value in obj_fields.iteritems():
                values = value.split(",")
                if "optional" in values:
                    values.remove("optional")
                if "primarykey" in values:
                    values.remove("primarykey")
                if "M2M" in values:
                    values.remove("M2M")
                if "O2M" in values:
                    values.remove("O2M")
                if values[0][0:1] == '$':
                    custom_classes.add(values[0][1:])

            if len(custom_classes) > 0:
                f.write('@class ' )
                i = 1
                for custom_class in custom_classes:
                    if i < len(custom_classes):
                        f.write(custom_class + ', ')
                    else:
                        f.write(custom_class + ';\n\n')
                    i += 1

            f.write('@interface ' + obj_name[1:] + ' : NSManagedObject\n\n')

            for key, value in obj_fields.iteritems():
                values = value.split(",")
                if "optional" in values:
                    values.remove("optional")
                if "primarykey" in values:
                    values.remove("primarykey")
                if "M2M" in values:
                    values.remove("M2M")
                if "O2M" in values:
                    values.remove("O2M")
                if values[0][0:1] == '$':
                    f.write('@property (nonatomic, strong) ' + values[0][1:] + ' *' + key + '\n')
                elif values[0] == "string":
                    f.write('@property (nonatomic, copy) ' + MODEL_DATA_TYPES[values[0]] + ' *' + key + '\n')
            f.write('\n')
            f.write('@end')

        with open(obj_name[1:] + ".m", "w") as f:
            f.write('//\n')
            f.write('// ' + obj_name[1:] + ".m\n")
            f.write('//\n')
            f.write('// Created by Manticom on ' + str( datetime.datetime.now() ) +'\n')
            f.write('// Copyright (c) ' + str(datetime.datetime.now().year) + ' Manticom. All rights reserved.\n')
            f.write('\n')

            f.write('#import ' + '"' + obj_name[1:] + '.h" \n\n')
            f.write('@implementation ' + obj_name[1:] + '\n\n')
            f.write('@dynamic ')
            obj_fields = obj[obj_name]
            i = 1
            for key, value in obj_fields.iteritems():
                values = value.split(",")
                if "optional" in values:
                    values.remove("optional")
                if "primarykey" in values:
                    values.remove("primarykey")
                if "M2M" in values:
                    values.remove("M2M")
                if "O2M" in values:
                    values.remove("O2M")
                if i < len(obj_fields.keys()):
                    f.write(key + ', ')
                else:
                    f.write(key + ';\n\n')
                i += 1

            f.write('@end')