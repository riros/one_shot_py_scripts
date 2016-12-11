# coding: cp1251
import xlsxwriter
import datetime
import re


class CBaseLib:
    _loaded = False
    _fields = []

    def __init__(self):
        self._fields = {}
        self._loaded = False

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
                self.__setattr__(k, re.search(v, s).groups()[0])
            except AttributeError:
                print('не найдено одно из полей %ы. %s = %s', self.__class__, k, v)
                self.__dict__[k] = None
        self.set_loaded()
        return self

    def __setattr__(self, key, value):
        if isinstance(value, ''.__class__) and len(value) <= 12:
            try:
                v = float(value)
            except:
                pass
            else:
                self.__dict__[key] = v
                return self
            if re.match('\d{2}.\d{2}.\d{4}', value):
                try:
                    self.__dict__[key] = datetime.datetime.strptime(value, '%d.%m.%Y').strftime('%Y-%m-%d')
                    return self
                except:
                    print("ошибка конвертации даты %s", value)
                    raise Exception()

        self.__dict__[key] = value

    @classmethod
    def is_loaded(cls):
        return cls._loaded

    @classmethod
    def set_loaded(cls, state=True):
        cls._loaded = state


class CBankStatementDoc(CBaseLib):
    """docstring for EDoc"""
    x_PayerINN = ''
    x_PayerAccount = ''
    x_RecipientAccount = ''

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
            doc_start = re.search("СекцияДокумент", s)
            doc_end = re.search("КонецДокумента", s)
            if doc_end and doc_start:
                str_DocSection = s[doc_start.span()[0]:doc_end.span()[0]]
                self.load_fields_from_string(str_DocSection)
                s = s[:doc_start.span()[0]] + s[doc_end.span()[1]:]
            else:
                self.set_loaded(False)
                break
            yield self


class CAccount(CBaseLib):
    """docstring for Account"""

    def __init__(self):
        super(CAccount, self).__init__()
        self.x_dateBegin = "\nДатаНачала=(.*)"
        self.x_dateEnd = "\nДатаКонца=(.*)"
        self.x_account = "\nРасчСчет=(.*)"
        self.x_balanceBegin = "НачальныйОстаток=(.*)"
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
        self.bank_statement_docs = iter([CBankStatementDoc])
        self.doc_ptr = CBankStatementDoc()

    def load_class_form_1CClientBankExchange_string(self, s):
        m = re.search("^1CClientBankExchange\n([^$]+)КонецФайла", s)
        if (m):
            """Исключаем из изсходной строки информацию о лицевом счете, и инициализируем класс"""
            ss = self.Account.extract_one(m.groups()[0])
            self.bank_statement_docs = self.doc_ptr.iterator_from_string(ss)
            self.load_fields_from_string(ss)
            if self.x_dateCraate and self.x_timeCreate:
                strdatetime = self.x_dateCraate + ' ' + self.x_timeCreate
                self.dateCraate = datetime.datetime.strptime(strdatetime, "%Y-%m-%d %H:%M:%S")
                self.set_loaded()
        else:
            raise Exception("не найден начальный и конечный тег файла. 1CClientBankExchange ... КонецФайла")

    def validate(self):
        if self.x_codepage == "Windows" and self.x_version == "1.02":
            return True
        else:
            raise Exception("несоответствие формата файла загрузки")

    def save_documents_to_xlsx(self, file_path):
        if not file_path:
            raise Exception('Не указано имя файла для экспорта')

        book = xlsxwriter.Workbook(file_path)
        in_sheet = book.add_worksheet("приход")
        out_sheet = book.add_worksheet('расход')
        first = True
        c, in_r, out_r = 0, 0, 0
        for doc in self.bank_statement_docs:
            if first:
                for k, v in doc.fields.items():
                    in_sheet.write(in_r, c, v)
                    out_sheet.write(out_r, c, v)
                    c += 1
                c = 0
                first = False
            if doc.x_RecipientAccount == self.x_account:
                in_r += 1
            else:
                out_r += 1
            for k, v in doc.fields.items():
                if doc.x_RecipientAccount == self.x_account:
                    in_sheet.write(in_r, c, doc.__dict__[k])
                else:
                    out_sheet.write(out_r, c, doc.__dict__[k])

                c += 1
            c = 0
        book.close()

    def is_loaded(self):
        return True if self.Account.is_loaded() and self._loaded else False


if __name__ == "__main__":
    # execute only if run as a script
    filename = "kikuban.txt"
    f = open(filename)
    filedata = f.read()
    f.close()
    bs = CBankStatement()
    bs.load_class_form_1CClientBankExchange_string(filedata)
    bs.save_documents_to_xlsx(filename + ".xlsx")
