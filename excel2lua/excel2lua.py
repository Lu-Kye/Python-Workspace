#!/usr/bin/env python
# encoding: utf-8

import datetime
import zipfile
import os
import xml.parsers.expat
from xml.dom import minidom
import re
import shutil

file_path = os.path.abspath(__file__).replace("excel2lua.py", "")
excels_path = os.path.join(file_path, "..")
luas_path = os.path.join(excels_path, "luas")
luas_table = "Table.txt"

# see also ruby-roo lib at: http://github.com/hmcgowan/roo
FORMATS = {
    'general': 'general',
    '0': 'general',
    '0.00': 'float',
    '#,##0': 'general',
    '#,##0.00': 'float',
    '0%': 'int_percentage',
    '0.0%': 'percentage',
    '0.00%': 'percentage',
    '0.00e+00': 'float',
    'mm-dd-yy': 'date',
    'd-mmm-yy': 'date',
    'd-mmm': 'date',
    'mmm-yy': 'date',
    'h:mm am/pm': 'date',
    'h:mm:ss am/pm': 'date',
    'h:mm': 'time',
    'h:mm:ss': 'time',
    'm/d/yy h:mm': 'date',
    '#,##0 ;(#,##0)': 'general',
    '#,##0 ;[red](#,##0)': 'general',
    '#,##0.00;(#,##0.00)': 'float',
    '#,##0.00;[red](#,##0.00)': 'float',
    'mm:ss': 'time',
    '[h]:mm:ss': 'time',
    'mmss.0': 'time',
    '##0.0e+0': 'float',
    '@': 'general',
    'yyyy\\-mm\\-dd': 'date',
    'dd/mm/yy': 'date',
    'hh:mm:ss': 'time',
    "dd/mm/yy\\ hh:mm": 'date',
    'dd/mm/yyyy hh:mm:ss': 'date',
    'yy-mm-dd': 'date',
    'd-mmm-yyyy': 'date',
    'm/d/yy': 'date',
    'm/d/yyyy': 'date',
    'dd-mmm-yyyy': 'date',
    'dd/mm/yyyy': 'date',
    'mm/dd/yy hh:mm am/pm': 'date',
    'mm/dd/yyyy hh:mm:ss': 'date',
    'yyyy-mm-dd hh:mm:ss': 'date',
}
STANDARD_FORMATS = {
    0: 'general',
    1: '0',
    2: '0.00',
    3: '#,##0',
    4: '#,##0.00',
    9: '0%',
    10: '0.00%',
    11: '0.00e+00',
    12: '# ?/?',
    13: '# ??/??',
    14: 'mm-dd-yy',
    15: 'd-mmm-yy',
    16: 'd-mmm',
    17: 'mmm-yy',
    18: 'h:mm am/pm',
    19: 'h:mm:ss am/pm',
    20: 'h:mm',
    21: 'h:mm:ss',
    22: 'm/d/yy h:mm',
    37: '#,##0 ;(#,##0)',
    38: '#,##0 ;[red](#,##0)',
    39: '#,##0.00;(#,##0.00)',
    40: '#,##0.00;[red](#,##0.00)',
    45: 'mm:ss',
    46: '[h]:mm:ss',
    47: 'mmss.0',
    48: '##0.0e+0',
    49: '@',
}

def print_error(msg):
    print '\033[1;31;40m'
    print msg
    print '\033[0m'

#
# usage: xlsx2csv("test.xslx", open("test.csv", "w+"))
# parameters:
# sheetid - sheet no to convert (0 for all sheets)
# dateformat - override date/time format
# delimiter - csv columns delimiter symbol
# sheet_delimiter - sheets delimiter used when processing all sheets
# skip_empty_lines - skip empty lines
#
def xlsx2sheets(infilepath):
    sheets = []
    dateformat = None
    skip_empty_lines = False
    ziphandle = zipfile.ZipFile(infilepath)

    try:
        shared_strings = parse(ziphandle, SharedStrings, "xl/sharedStrings.xml")
        styles = parse(ziphandle, Styles, "xl/styles.xml")
        workbook = parse(ziphandle, Workbook, "xl/workbook.xml")
        for s in workbook.sheets:
            sheet = Sheet(workbook, s['name'], shared_strings, styles,
                          ziphandle.read("xl/worksheets/sheet%i.xml" % s['id']))
            sheet.set_dateformat(dateformat)
            sheet.set_skip_empty_lines(skip_empty_lines)
            sheet.parse()
            sheets.append(sheet)
    finally:
        ziphandle.close()
    return sheets


def parse(ziphandle, klass, filename):
    instance = klass()
    if filename in ziphandle.namelist():
        instance.parse(ziphandle.read(filename))
    return instance


class Workbook:
    def __init__(self):
        self.sheets = []
        self.date1904 = False

    def parse(self, data):
        workbookDoc = minidom.parseString(data)
        if len(workbookDoc.firstChild.getElementsByTagName("fileVersion")) == 0:
            self.appName = 'unknown'
        else:
            self.appName = workbookDoc.firstChild.getElementsByTagName("fileVersion")[0]._attrs['appName'].value
        try:
            self.date1904 = workbookDoc.firstChild.getElementsByTagName("workbookPr")[0]._attrs[
                                'date1904'].value.lower().strip() != "false"
        except:
            pass

        sheets = workbookDoc.firstChild.getElementsByTagName("sheets")[0]
        for sheetNode in sheets.getElementsByTagName("sheet"):
            attrs = sheetNode._attrs
            name = attrs["name"].value
            if self.appName == 'xl':
                if 'r:id' in attrs:
                    id = int(attrs["r:id"].value[3:])
                else:
                    id = int(attrs['sheetId'].value)
            else:
                if 'sheetId' in attrs:
                    id = int(attrs["sheetId"].value)
                else:
                    id = int(attrs['r:id'].value[3:])
            self.sheets.append({'name': name, 'id': id})


class Styles:
    def __init__(self):
        self.numFmts = {}
        self.cellXfs = []

    def parse(self, data):
        styles = minidom.parseString(data).firstChild
        # numFmts
        numFmtsElement = styles.getElementsByTagName("numFmts")
        if len(numFmtsElement) == 1:
            for numFmt in numFmtsElement[0].childNodes:
                numFmtId = int(numFmt._attrs['numFmtId'].value)
                formatCode = numFmt._attrs['formatCode'].value.lower().replace('\\', '')
                self.numFmts[numFmtId] = formatCode
        # cellXfs
        cellXfsElement = styles.getElementsByTagName("cellXfs")
        if len(cellXfsElement) == 1:
            for cellXfs in cellXfsElement[0].childNodes:
                if (cellXfs.nodeName != "xf"):
                    continue
                numFmtId = int(cellXfs._attrs['numFmtId'].value)
                self.cellXfs.append(numFmtId)


class SharedStrings:
    def __init__(self):
        self.parser = None
        self.strings = []
        self.si = False
        self.t = False
        self.rPh = False
        self.value = ""

    def parse(self, data):
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.CharacterDataHandler = self.handleCharData
        self.parser.StartElementHandler = self.handleStartElement
        self.parser.EndElementHandler = self.handleEndElement
        self.parser.Parse(data)

    def handleCharData(self, data):
        if self.t:
            self.value += data

    def handleStartElement(self, name, attrs):
        if name == 'si':
            self.si = True
            self.value = ""
        elif name == 't' and self.rPh:
            self.t = False
        elif name == 't' and self.si:
            self.t = True
        elif name == 'rPh':
            self.rPh = True

    def handleEndElement(self, name):
        if name == 'si':
            self.si = False
            self.strings.append(self.value)
        elif name == 't':
            self.t = False
        elif name == 'rPh':
            self.rPh = False


class Sheet:
    def __init__(self, workbook, name, sharedString, styles, data):
        self.parser = None

        # TODO custom add
        self.name = name
        self.datas = []

        self.sharedString = None
        self.styles = None

        self.in_sheet = False
        self.in_row = False
        self.in_cell = False
        self.in_cell_value = False
        self.in_cell_formula = False

        self.columns = {}
        self.rowNum = None
        self.colType = None
        self.s_attr = None
        self.data = None

        self.dateformat = None
        self.skip_empty_lines = False

        self.data = data
        self.workbook = workbook
        self.sharedStrings = sharedString.strings
        self.styles = styles

    def set_dateformat(self, dateformat):
        self.dateformat = dateformat

    def set_skip_empty_lines(self, skip):
        self.skip_empty_lines = skip

    def parse(self):
        self.parser = xml.parsers.expat.ParserCreate()
        self.parser.CharacterDataHandler = self.handleCharData
        self.parser.StartElementHandler = self.handleStartElement
        self.parser.EndElementHandler = self.handleEndElement
        self.parser.Parse(self.data)

    def handleCharData(self, data):
        if self.in_cell_value:
            try:
                self.data = ('%f' % float(data)).rstrip('0').rstrip('.')  # default value
            except:
                self.data = data  # default value
            if self.colType == "s":  # shared string
                self.data = self.sharedStrings[int(data)]
            elif self.colType == "b":  # boolean
                self.data = (int(data) == 1 and "TRUE") or (int(data) == 0 and "FALSE") or data
            elif self.s_attr:
                s = int(self.s_attr)

                # get cell format
                format = None
                xfs_numfmt = self.styles.cellXfs[s]
                if xfs_numfmt in self.styles.numFmts:
                    format = self.styles.numFmts[xfs_numfmt]
                elif xfs_numfmt in STANDARD_FORMATS:
                    format = STANDARD_FORMATS[xfs_numfmt]
                # get format type
                if format and format in FORMATS:
                    format_type = FORMATS[format]

                    if format_type == 'date':  # date/time
                        try:
                            if self.workbook.date1904:
                                date = datetime.datetime(1904, 01, 01) + datetime.timedelta(float(data))
                            else:
                                date = datetime.datetime(1899, 12, 30) + datetime.timedelta(float(data))
                            if self.dateformat:
                                # str(dateformat) - python2.5 bug, see: http://bugs.python.org/issue2782
                                self.data = date.strftime(str(self.dateformat))
                            else:
                                dateformat = format.replace("yyyy", "%Y").replace("yy", "%y"). \
                                    replace("hh:mm", "%H:%M").replace("h", "%H").replace("%H%H", "%H").replace("ss",
                                                                                                               "%S"). \
                                    replace("d", "%e").replace("%e%e", "%d"). \
                                    replace("mmmm", "%B").replace("mmm", "%b").replace(":mm", ":%M").replace("m",
                                                                                                             "%m").replace(
                                    "%m%m", "%m"). \
                                    replace("am/pm", "%p")
                                self.data = date.strftime(str(dateformat)).strip()
                        except (ValueError, OverflowError):
                            # invalid date format
                            self.data = data
                    elif format_type == 'time':  # time
                        self.data = ('%f' % (float(data) * 24 * 60 * 60)).rstrip('0').rstrip('.')
                    elif format_type == 'int_percentage':
                        self.data = str(int(float(data) * 100.0 + 0.5)) + '%'
                    elif format_type == 'percentage':
                        self.data = ('%f' % (float(data) * 100.0)).rstrip('0').rstrip('.') + '%'
                        # does not support it
                        # elif self.in_cell_formula:
                        #    self.formula = data

    def handleStartElement(self, name, attrs):
        if self.in_row and name == 'c':
            self.colType = attrs.get("t")
            self.s_attr = attrs.get("s")
            cellId = attrs.get("r")
            if cellId:
                self.colNum = cellId[:len(cellId) - len(self.rowNum)]
                self.colIndex = 0
            else:
                self.colIndex += 1
            # self.formula = None
            self.data = ""
            self.in_cell = True
        elif self.in_cell and name == 'v':
            self.in_cell_value = True
        # elif self.in_cell and name == 'f':
        #    self.in_cell_formula = True
        elif self.in_sheet and name == 'row' and 'r' in attrs:
            self.rowNum = attrs['r']
            self.in_row = True
            self.columns = {}
            self.spans = None
            if 'spans' in attrs:
                self.spans = [int(i) for i in attrs['spans'].split(":")]
        elif name == 'sheetData':
            self.in_sheet = True

    def handleEndElement(self, name):
        if self.in_cell and name == 'v':
            self.in_cell_value = False
        # elif self.in_cell and name == 'f':
        #    self.in_cell_formula = False
        elif self.in_cell and name == 'c':
            t = 0
            for i in self.colNum:
                t = t * 26 + ord(i) - 64
            self.columns[t - 1 + self.colIndex] = self.data
            self.in_cell = False
        if self.in_row and name == 'row':
            if len(self.columns.keys()) > 0:
                d = [""] * (max(self.columns.keys()) + 1)
                for k in self.columns.keys():
                    d[k] = self.columns[k].encode("utf-8")
                if self.spans:
                    l = self.spans[0] + self.spans[1] - 1
                    if len(d) < l:
                        d += (l - len(d)) * ['']
                # write line to csv
                if not self.skip_empty_lines or d.count('') != len(d):
                    self.datas.append(d)
                    # self.writer.writerow(d)
            self.in_row = False
        elif self.in_sheet and name == 'sheetData':
            self.in_sheet = False


class Table:
    def __init__(self, name, sheet):
        self.file_name = name + ".xlsx"
        self.name = "Table_" + re.sub(r'\W', "_", name)
        self.sheet = sheet
        self.datas_config = []
        self.datas = []
        self.success = self.parse()

    # parse sheet datas
    # 0 is properties chinese name
    # 1 is properties english name
    # 2 is properties type { number, string }
    def parse(self):
        datas = self.sheet.datas

        num = min(len(datas[0]), len(datas[1]), len(datas[2]))
        valid_num = 0
        invalid_num = num
        for i in range(0, num):
            data_config = {
                "cname": str(datas[0][i]),
                "ename": re.sub(r'\W', "_", str(datas[1][i])),
                "type": re.sub(r'\W', "_", str(datas[2][i]))
            }

            m = re.match(r'\S*[a-zA-Z]+\S*', data_config["ename"])
            if m:
                self.datas_config.append(data_config)
                valid_num = i
            else:
                invalid_num = i

            if valid_num > invalid_num:
                return False

        for i in range(3, len(datas)):
            self.datas.append(datas[i])

        return True

    # get value
    def get_value(self, value, type):
        if value is None or type is None:
            return "nil"

        if type == "number":
            try:
                return str(int(value))
            except:
                try:
                    return str(float(value))
                except:
                    return "nil"
        elif type == "string":
            s = str(value).replace("\\", "\\\\")
            s = s.replace("\n", "\\n")
            s = s.replace("\r", "\\n")
            return '"' + s + '"'
        else:
            return "nil"

    # write datas to file
    def write_lua(self, outpath):
        # generate lua object
        data = self.name + " = { \n"
        all_num = len(self.datas_config)

        for values in self.datas:
            for i in range(0, all_num):
                value = None
                try:
                    value = values[i]
                except:
                    value = None

                config = self.datas_config[i]

                ename = config['ename']
                type = config['type']

                if i == 0:
                    ename_value = self.get_value(value, "number")
                    if ename_value is "nil":
                        break
                    data += "\t[" + ename_value + "] = {"
                else:
                    data += ename + " = " + self.get_value(value, type)

                if i == (all_num - 1):
                    data += "}"
                    if self.datas.index(values) == (len(self.datas) - 1):
                        data += " \n"
                    else:
                        data += ", \n"
                elif i != 0:
                    data += ", "

        data += "} \n"

        file_path = outpath + "/" + self.name + ".txt"
        print("write file : " + file_path)
        file = open(file_path, "wb")
        file.write(data)
        file.close()


if __name__ == "__main__":
    print("start generate...")
    print("excels path: " + excels_path)
    print("luas path" + luas_path)

    try:
        shutil.rmtree(luas_path)
    except:
        pass

    try:
        os.mkdir(luas_path)
    except:
        pass

    # generate tables
    tables = []
    for p, d, fs in os.walk(excels_path):
        for f in fs:
            m = re.match(r'.*\.xlsx', f)
            if not m:
                continue

            infile = p + "/" + f
            outfile = p.replace(excels_path, luas_path) + "/" + f.replace(".xlsx", ".txt")
            sheets = xlsx2sheets(infile)

            print("parse file to sheet : " + f)

            # only parse sheet 0
            sheet = sheets[0]

            # print("parse sheet to table : " + sheet.name)

            table = Table(f.replace(".xlsx", ""), sheet)
            if table.success:
                table.write_lua(luas_path)
                tables.append(table)
            else:
                print_error(table.file_name + " 配置错误：存在空的字段名或字段类型！！！")
        break

    # lua include
    data = ""
    for table in tables:
        data += "autoImport('" + table.name + "') \n"
    file_path = luas_path + "/" + luas_table
    print("write file : " + file_path)
    file = open(file_path, "wb")
    file.write(data)
    file.close()