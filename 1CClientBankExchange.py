# coding: cp1251
import xlsxwriter
import datetime
import re

"""
TODO 1) Сделать авто конвертацию дат и времени на сеттерах. если в имени атрибута есть date
"""
class CBaseLib:
    def __init__(self):
        self._fields = {}
        self.loaded = False

    @property
    def fields(self):
        """Список полей для загрузки из файла"""
        if len(self._fields) > 0:
            return self._fields
        else:
            for i in self.__dict__.keys():
                if re.match('x_\w+', i):
                    self._fields[i] = self.__dict__[i]
            return self._fields

    def load_fields_from_string(self, s):
        for k, v in self.fields.items():
            try:
                self.__dict__[k] = re.search(v, s).groups()[0]
            except AttributeError:
                print('не найдено одно из полей %ы. %s = %s', self.__class__, k, v)
                self.__dict__[k] = None
        return self


class CBankStatementDoc(CBaseLib):
    """docstring for EDoc"""

    def __init__(self):
        super(CBankStatementDoc, self).__init__()
        self.x_DocName = "СекцияДокумент=(.*)"
        self.x_Num = "\nНомер=(\d+)"
        self.x_Date = "\nДата=(.+)"
        self.x_Code = "\nКод=(.*)"
        self.x_Summ = "\nСумма=(.+)"

        self.x_PaymentDescription = "\nНазначениеПлатежа=(.*)"
        self.x_PayType = "\nВидОплаты=(.*)"
        self.x_PaymentТerminate = "\nСрокПлатежа=(.*)"
        self.x_Order = "\nОчередность=(.*)"

        self.x_PayerName = "\nПлательщик1=(.*)"
        self.x_PayerAccount = "\nПлательщикСчет=(.*)"
        self.x_PayerINN = "\nПлательщикИНН=(.*)"
        self.x_PayerKPP = "\nПлательщикКПП=(.*)"
        self.x_PayerBIK = "\nПлательщикБИК=(.*)"
        self.x_PayerCorAccount = "\nПлательщикКорсчет=(.*)"
        self.x_PayerBank1 = "\nПлательщикБанк1=(.*)"
        # x_PayerPayAccount = 0
        # x_PayerDebitDate = datetime.date.today()
        # self.x_PayTypeName = "\nЭлектронно="

        self.x_Recipient = "\nПолучатель1=(.*)"
        self.x_RecipientAccount = "\nПолучательСчет=(.*)"
        self.x_RecipientINN = "\nПолучательИНН=(.*)"
        self.x_RecipientBIK = "\nПолучательБИК=(.*)"
        self.x_RecipientCorAccount = "\nПолучательСчет=(.*)"
        self.x_RecipientKPP = "\nПолучательКПП=(.*)"
        self.x_RecipientBank = "\nПолучательБанк1=(.*)"

        self.x_indexKBK = "\nПоказательКБК=(.*)"
        self.x_OKATO = "\nОКАТО=(.*)"
        self.x_indexSource = "\nПоказательОснования=(.*)"
        self.x_indexPeriod = "\nПоказательПериода=(.*)"
        self.x_indexNum = "\nПоказательНомера=(.*)"
        self.x_indexDate = "\nПоказательДаты=(.*)"
        self.x_indexType = "\nПоказательТипа=(.*)"

    def validate(self):
        if self.x_Num == 0:
            return False
        return True

    def iterator_from_string(self, src_str):
        s = src_str[:]
        while True:
            docStart = re.search("СекцияДокумент", s)
            docEnd = re.search("КонецДокумента", s)
            if docEnd and docStart:
                str_DocSection = s[docStart.span()[0]:docEnd.span()[0]]
                self.load_fields_from_string(str_DocSection)
                s = s[:docStart.span()[0]] + s[docEnd.span()[1]:]
            else:
                break
            yield self


class CAccount(CBaseLib):
    """docstring for Account"""

    def __init__(self):
        super(CAccount, self).__init__()
        self.x_dateBegin = "\nДатаНачала=(.*)"
        self.x_dateEnd = "\nДатаКонца=(.*)"
        self.x_account = "\nРасчСчет=(.*)"
        self.x_balanceBegin = "\nНачальныйОстаток=(.*)"
        self.x_amount_summ = "\nВсегоПоступило=(.*)"
        self.x_discarded_summ = "\nВсегоСписано=(.*)"
        self.x_balanceEnd = "\nКонечныйОстаток=(.*)"

    def extract_one(self, s):
        """извлекает из сроки секцию, удаляет ее из исходной,и инициализирует класс данными из этой секции"""
        sr = re.search("СекцияРасчСчет[^$]+КонецРасчСчет", s)
        if sr:
            s_account = s[sr.span()[0]:sr.span()[1]]
            self.load_fields_from_string(s_account)
        else:
            raise Exception('Не найдена СекцияРасчСчет([^$])КонецРасчСчет')
        return s[:sr.span()[0]] + s[sr.span()[1]:]


class CBankStatement(CBaseLib):
    """docstring for BankStatement"""
    """TODO: настройка кодировки файла"""
    def __init__(self):
        super(CBankStatement, self).__init__()
        self.x_codepage = 'Кодировка=(.*)'
        self.x_version = 'ВерсияФормата=(.*)'
        self.x_dateBegin = '\nДатаНачала=(.*)'
        self.x_dateEnd = '\nДатаКонца=(.*)'
        self.x_dateCraate = '\nДатаСоздания=(.*)'
        self.x_timeCreate = '\nВремяСоздания=(.*)'
        self.x_account = 'РасчСчет=(.+)'

        self.Account = CAccount()
        self.bank_statement_docs = iter([])
        self.doc_ptr = CBankStatementDoc()

    def load_class_form_1CClientBankExchange_string(self, s):
        m = re.search("^1CClientBankExchange\n([^$]+)КонецФайла", s)
        if (m):
            """Исключаем из изсходной строки информацию о лицевом счете, и инициализируем класс"""
            ss = self.Account.extract_one(m.groups()[0])
            self.bank_statement_docs = self.doc_ptr.iterator_from_string(ss)
            self.load_fields_from_string(ss)
            strdatetime = self.x_dateCraate + ' ' + self.x_timeCreate
            """25.10.2016 16:22:44"""
            self.dateCraate = datetime.datetime.strptime(strdatetime, "%d.%m.%Y %H:%M:%S")
        else:
            raise Exception("не найден начальный и конечный тег файла. 1CClientBankExchange ... КонецФайла")


    def validate(self):
        return True
        if self.codepage == "Windows" and self.version == "1.02":
            return True
        else:
            raise Exception("несоответствие формата файла загрузки")

    def save_Documents_to_xlsx(self, filepath):
        if not filepath:
            raise Exception('Не указано имя файла для экспорта')

        book = xlsxwriter.Workbook(filepath)
        sheet = book.add_worksheet()
        first = True
        c, r = 0, 0
        for doc in self.bank_statement_docs:
            if first:
                for k, v in doc.fields.items():
                    sheet.write(r, c, v)
                    c += 1
                c = 0
                first = False
            else:
                r += 1
                for k, v in doc.fields.items():
                    sheet.write(r, c, doc.__dict__[k])
                    c += 1
                c = 0
        book.close()


if __name__ == "__main__":
    # execute only if run as a script
    filename = "kikuban"
    f = open(filename)
    filedata = f.read()
    f.close()
    bs = CBankStatement()
    bs.load_class_form_1CClientBankExchange_string(filedata)
    bs.save_Documents_to_xlsx(filename + ".xlsx")
