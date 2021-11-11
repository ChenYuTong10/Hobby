from bs4 import BeautifulSoup
import urllib.request
import urllib.error
import re
import sqlite3

# 匹配模板
# "\u4E00-\u9FA5"为Unicode中中文字符的编码范围
project_pattern = re.compile(r'<td align="center" class="gvCell dxgv".*?>([^\s]*?)</td>')

projects = []


def main():
    # 准备工作
    database_save_path = u"广州大学实验数据.db"
    initializeDatabase(database_save_path)  # 初始化数据库
    # 获取数据
    for page in range(0, 9):
        html = requestURL(page)
    # 处理数据
        analyzeData(html)
    # 存入数据库
    saveAsDatabase(database_save_path)
    # 2021.9.21实验数据


# 请求数据
def requestURL(page):
    des_url = "http://202.192.67.23/_GD002_Teaching_Teaching/Teaching_SYAdvanceStudentList.aspx"
    request_header = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Cookie": "ASP.NET_SessionId=2e3pdmwadai4rpwelugfvowq; forums=BC92F730313290B8A8A0E744734897C63A21A63B30EEAC0722D1787E651D2D92D0C935B08DD7D9F0990E65A7C2D1A4256AE5813C70524BD27F57B39210700DF080612466E236E14CAA0C80DD25213098F9A26758A11988C98DBFFBEA216E666FDE0D21F78AE4E670788B036A738C5D37EFEE2DAAFE8AF3DFE91E39ABC5F1074F4B063BC4DCD32D2B35FB2B74E0092B03977172A80F25A9FD1F06F1F449365308779B8EEB084E128287FF04F3E31B9B19132062D7735CF1F2D22ED199676DCFBE954173C0E45E63F4A745B37E9626C792301FC78CAE362C58761DEF688234295D6DC73E8B1A1EED9974A13B762FD3C88FD49C7B048FE64093257AB03808DFBCA6688F87A019A1A806B3A8DBC23E89DD39DE07A3587F682BF01E061BDC44E0D83ACF96DF1AEB4FCDEDAE5495401E9FFCE28BF698F085D5F5D3452E45B8B287344018B8BF05DA27F3AA95162688B21FEEB9597B166CA4E32E01F29F4FD75C1650F7B25608C0565B94F1F2F7C2C447B3D7CFDE95465AE57CB53EF34ECB0DEB64C1B1F1CA1C9BFFC59C30AA88A55A70EE7F2725189F7770D7FF21E229CAC362CEEC042D392F6FE97C6D77E982AE9AA256A5443AA69F8004104DAFDBB7E72ABCF2066C19C15369CD466B186FBCF58345B17B8E7C123EBE58E08592E48E24D7A53D518868F4F01508E2CAFEA468275A01F4F0B3; UserName=2006300072; ThemeName=; IsFirstLogin=; System=LastActionTime=2021-09-21 12:29:21",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/93.0.4577.63 Safari/537.36 Edg/93.0.961.44 "
    }
    # 经过测试,已下四个参数不可缺少,其中第四个参数的最后一个数字决定了表格的页数
    request_data = bytes(urllib.parse.urlencode({
        "__VIEWSTATE": "/wEPDwUJNDA1MDAzODI5DxYCHhlPcGVuX0FkdmFuY2VFeHBDb3VudFZhbHVlBQEwFgJmD2QWAgIBD2QWCgIFDw9kFgIeB29uY2xpY2sFIEhlbHBTaG93KCdfR0QwMDJfT1AxMTEwJywnTGlzdCcpZAIJDzwrAAgBAA8WAh4HVmlzaWJsZWhkZAILDzwrAAkBAA8WAh4OXyFVc2VWaWV3U3RhdGVnZGQCDQ9kFgZmDzwrAAgBAA8WBB4OQWN0aXZlVGFiSW5kZXhmHwNnZGQCBA88KwAJAQAPFgIfA2dkFgICAQ9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAmYPZBYCZg9kFgJmD2QWAgIBDxQrAAUPFgIeD0RhdGFTb3VyY2VCb3VuZGdkZGQUKwAGFgQeD1JlcGVhdERpcmVjdGlvbgsqKVN5c3RlbS5XZWIuVUkuV2ViQ29udHJvbHMuUmVwZWF0RGlyZWN0aW9uAR4NUmVwZWF0Q29sdW1ucwICZGRkZA8WAh4KSXNTYXZlZEFsbGcPFCsADRQrAAEWBh4EVGV4dAUG6aKE57qmHgVWYWx1ZQUHQWR2YW5jZR4OUnVudGltZUNyZWF0ZWRnFCsAARYGHwkFDOmZouezu+WQjeensB8KBQtDb2xsZWdlTmFtZR8LZxQrAAEWBh8JBQnlrp7pqozlrqQfCgUORGVwYXJ0bWVudE5hbWUfC2cUKwABFgYfCQUM5a6e6aqM6aG555uuHwoFCFNZTUNJbmZvHwtnFCsAARYGHwkFDOW8gOaUvuWvueixoR8KBQlDbGFzc05hbWUfC2cUKwABFgYfCQUM5oyH5a+85pWZ5biIHwoFC1RlYWNoZXJOYW1lHwtnFCsAARYGHwkFDOiBlOezu+eUteivnR8KBQVQaG9uZR8LZxQrAAEWBh8JBQzlrp7pqozkurrlkZgfCgUNU1lUZWFjaGVyTmFtZR8LZxQrAAEWBh8JBRnml7bpl7Qo5ZGoL+aYn+acny/oioLmrKEpHwoFBlNKSW5mbx8LZxQrAAEWBh8JBQzlrp7pqozlnLDngrkfCgUIUm9vbU5hbWUfC2cUKwABFgYfCQUP5a6e6aqM5oyH5a+85LmmHwoFB0ZpbGVVcmwfC2cUKwABFgYfCQUM5Lq65pWw5bey5ruhHwoFC0FkdmFuY2VGdWxsHwtnFCsAARYGHwkFCeWItuWumuS6uh8KBQ9BcHBseVBlcnNvbk5hbWUfC2dkFg0FB0FkdmFuY2UFC0NvbGxlZ2VOYW1lBQ5EZXBhcnRtZW50TmFtZQUIU1lNQ0luZm8FCUNsYXNzTmFtZQULVGVhY2hlck5hbWUFBVBob25lBQ1TWVRlYWNoZXJOYW1lBQZTSkluZm8FCFJvb21OYW1lBQdGaWxlVXJsBQtBZHZhbmNlRnVsbAUPQXBwbHlQZXJzb25OYW1lZAIFD2QWAmYPZBYCZg9kFgJmD2QWAgIHDzwrABgDAA8WAh8FZ2QGD2QQFhECAQICAgMCBAIFAgYCBwIIAgkCCgILAgwCDQIOAg8CEAIRFhE8KwAKAgAWAh4PQ29sVmlzaWJsZUluZGV4AgEJFCsAARYCHhNBdXRvRmlsdGVyQ29uZGl0aW9uAgM8KwAKAgAWAh8MAgIJFCsAARYCHw0CAzwrAAoCABYCHwwCAwkUKwABFgIfDQIDPCsACgIAFgIfDAIECRQrAAEWAh8NAgM8KwAKAgAWAh8MAgUJFCsAARYCHw0CAzwrAAoCABYCHwwCBgkUKwABFgIfDQIDPCsACgIAFgIfDAIHCRQrAAEWAh8NAgM8KwAKAgAWAh8MAggJFCsAARYCHw0CAzwrAAoCABYCHwwCCQkUKwABFgIfDQIDPCsACgIAFgIfDAIKCRQrAAEWAh8NAgM8KwAKAgAWAh8MAgsJFCsAARYCHw0CAzwrAAoCABYCHwwCDAkUKwABFgIfDQIDPCsACgIAFgIfDAINCRQrAAEWAh8NAgM8KwAKAQkUKwABFgIfDQIDPCsACgEJFCsAARYCHw0CAzwrAAoBCRQrAAEWAh8NAgM8KwAKAQkUKwABFgIfDQIDDxYRAgECAQIBAgECAQIBAgECAQIBAgECAQIBAgECAQIBAgECARYBBYgBRGV2RXhwcmVzcy5XZWIuQVNQeEdyaWRWaWV3LkdyaWRWaWV3RGF0YUNvbHVtbiwgRGV2RXhwcmVzcy5XZWIudjEyLjIsIFZlcnNpb249MTIuMi41LjAsIEN1bHR1cmU9bmV1dHJhbCwgUHVibGljS2V5VG9rZW49Yjg4ZDE3NTRkNzAwZTQ5YRU8KwAGAQUUKwACZGRkAg8PPCsAFAIADxYCHwVnZAYPZBAWAWYWATwrAAgBABYCHwxmDxYBAgEWAQWVAURldkV4cHJlc3MuV2ViLkFTUHhUcmVlTGlzdC5UcmVlTGlzdERhdGFDb2x1bW4sIERldkV4cHJlc3MuV2ViLkFTUHhUcmVlTGlzdC52MTIuMiwgVmVyc2lvbj0xMi4yLjUuMCwgQ3VsdHVyZT1uZXV0cmFsLCBQdWJsaWNLZXlUb2tlbj1iODhkMTc1NGQ3MDBlNDlhZBgBBR5fX0NvbnRyb2xzUmVxdWlyZVBvc3RCYWNrS2V5X18WEwUSY3RsMDAkQVNQeFBDb250cm9sBSZjdGwwMCRBU1B4UENvbnRyb2wkVFBDSG0xJGJ0blBvcHVwSGVscAUpY3RsMDAkQVNQeFBDb250cm9sJFRQQ0htMSRidG5Qb3B1cE1heG1pemUFJ2N0bDAwJEFTUHhQQ29udHJvbCRUUENIbTEkYnRuUG9wdXBDbG9zZQUgY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSRBc3B4VEMFI2N0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkQVNQeE1lbnUyBTpjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJEFTUHhDYWxsYmFja1BhbmVsMSRBU1B4R3JpZFZpZXcxBUxjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJEFTUHhDYWxsYmFja1BhbmVsMSRBU1B4R3JpZFZpZXcxJERYUGFnZXJCb3R0b20kUFNQBThjdGwwMCRDb250ZW50UGxhY2VIb2xkZXIxJEFTUHhDYWxsYmFja1BhbmVsMiRwY1NlbGVjdFNwZQVHY3RsMDAkQ29udGVudFBsYWNlSG9sZGVyMSRBU1B4Q2FsbGJhY2tQYW5lbDIkcGNTZWxlY3RTcGUkYnRuU2VsZWN0U3BlT0sFS2N0bDAwJENvbnRlbnRQbGFjZUhvbGRlcjEkQVNQeENhbGxiYWNrUGFuZWwyJHBjU2VsZWN0U3BlJGJ0blNlbGVjdFNwZUNhbmNlbAUPY3RsMDAkQVNQeFBDVGlwBR1jdGwwMCRNZXNzYWdlQm94MSRBU1B4UENBbGVydAUuY3RsMDAkTWVzc2FnZUJveDEkQVNQeFBDQWxlcnQkVFBDQzAkYnRuQWxlcnRPSwUyY3RsMDAkTWVzc2FnZUJveDEkQVNQeFBDQWxlcnQkVFBDQzEkYnRuQ29uZmlybU9LXzEFNmN0bDAwJE1lc3NhZ2VCb3gxJEFTUHhQQ0FsZXJ0JFRQQ0MxJGJ0bkNvbmZpcm1DYW5jZWxfMQUzY3RsMDAkTWVzc2FnZUJveDEkQVNQeFBDQWxlcnQkVFBDQzIkYnRuQ29uZmlybVllc18yBTJjdGwwMCRNZXNzYWdlQm94MSRBU1B4UENBbGVydCRUUENDMiRidG5Db25maXJtTm9fMgU2Y3RsMDAkTWVzc2FnZUJveDEkQVNQeFBDQWxlcnQkVFBDQzIkYnRuQ29uZmlybUNhbmNlbF8y8E8GaIDw8KOuFbx4oTTFaph1a76jU7cNOQt8lkA5maA=",
        "ctl00$ContentPlaceHolder1$ASPxCallbackPanel1$ASPxGridView1$CallbackState": "BwQHAgIERGF0YQZsIQAAAABWAAAAVgAAADIAAAAZAAAAAA4AAAACSUQCSUQDAAAIU1lNQ0luZm8JU1lNQyBJbmZvBwAACUNsYXNzTmFtZQpDbGFzcyBOYW1lBwAAC1RlYWNoZXJOYW1lDFRlYWNoZXIgTmFtZQcAAA9BcHBseVBlcnNvbk5hbWURQXBwbHkgUGVyc29uIE5hbWUHAAAIWE5YUUNvZGUJWE5YUSBDb2RlAwAABFNZSUQEU1lJRAMAAAZTSkluZm8HU0ogSW5mbwcAAAlQYXNzU3RhdGUKUGFzcyBTdGF0ZQMAAAtDb2xsZWdlTmFtZQxDb2xsZWdlIE5hbWUHAAAORGVwYXJ0bWVudE5hbWUPRGVwYXJ0bWVudCBOYW1lBwAADVNZVGVhY2hlck5hbWUPU1kgVGVhY2hlciBOYW1lBwAAC0FkdmFuY2VGdWxsDEFkdmFuY2UgRnVsbAMAAAVQaG9uZQVQaG9uZQcAACMAAAAEVGhpcxBTdGF0ZURlZmF1bHRUZXh0DVBhc3NTdGF0ZVRleHQLQXVkaXRSb2xlSUQNQXVkaXRPYmplY3RJRAZLQ0luZm8ETVpSUwRLQ0lEA0tDSAdDbGFzc0lECVRlYWNoZXJJRA9SaWdodHNUZWFjaGVySUQLU1lUZWFjaGVySUQEUENJRARTWVhIDUFwcGx5UGVyc29uSUQNQXBwbHlEYXRlVGltZQNLQ00ES0NYUwRTWU1DBFNZWFMCUEMEVHlwZQ1SZXBlYXRBZHZhbmNlD0V4YW1pbmF0aW9uQm9vaxFDb25mbGljdHNEb250U2F2ZQ5BdWRpdFBhc3NTdGF0ZQtBZGp1c3RTdGF0ZQhPcGVuVHlwZQhBdHREZXBJRAlDb2xsZWdlSUQHRmlsZVVybAZSZW1hcmsOU2NvcmVTdGF0ZVRleHQKU2NvcmVTdGF0ZQcABwAHAAcABv//AwYUEwcCLygxMTAyMDIwMDcp5Y+Y5rip57KY5rue57O75pWw55qE5rWL5a6aWzPlrabml7ZdCQcCBumprOmilgcCBumprOmilgMG9E4DBoQMBwIzMTEtMTLlkagv5pif5pyf5LiALzktMTHoioIKMTLlkagv5pif5pyf5LiJLzktMTHoioIKAwdjBwIb54mp55CG5LiO5p2Q5paZ56eR5a2m5a2m6ZmiBwIW5aSn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pKflrabniannkIblrp7pqow25a6kCQMHAQkHAAcABv//AwYnEwcCJigxMTAyMDA0MDIp55S15L2N5beu6K6h5L2/55SoWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBo4MBwIXMTTlkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAQkHAAcABv//AwYoEwcCLygxMTAyMDIyMDEp56m65rCU5Lit6LaF5aOw6YCf55qE5rWL6YePWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBpoMBwIXMTXlkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAQkHAAcABv//AwYpEwcCJigxMTAyMDA0MDIp55S15L2N5beu6K6h5L2/55SoWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBo4MBwIXMTXlkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAQkHAAcABv//AwYqEwcCLygxMTAyMDIyMDEp56m65rCU5Lit6LaF5aOw6YCf55qE5rWL6YePWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBpoMBwIXMTblkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAQkHAAcABv//AwYrEwcCJigxMTAyMDA0MDIp55S15L2N5beu6K6h5L2/55SoWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBo4MBwIXMTblkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAQkHAAcABv//AwYsEwcCLygxMTAyMDIyMDEp56m65rCU5Lit6LaF5aOw6YCf55qE5rWL6YePWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBpoMBwIXMTflkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAQkHAAcABv//AwYtEwcCJigxMTAyMDA0MDIp55S15L2N5beu6K6h5L2/55SoWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBo4MBwIXMTflkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAAkHAAcABv//AwYuEwcCLygxMTAyMDIyMDEp56m65rCU5Lit6LaF5aOw6YCf55qE5rWL6YePWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBpoMBwIXMTjlkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAAkHAAcABv//AwYvEwcCJigxMTAyMDA0MDIp55S15L2N5beu6K6h5L2/55SoWzPlrabml7ZdBwKZAeeOr+W3pTIwMVsyN10s546v5belMjAyWzI4XSznjq/lt6UyMDNbMzJdLOiuoeenkTIwMVs0MV0s6K6h56eRMjAyWzQwXSzova/ku7YyMDFbNDBdLOi9r+S7tjIwMls0MF0s5py65qKwMjAzWzQxXSzmnLrmorAyMDRbNDBdLOeUteawlDIwMVszN10s55S15rCUMjAyWzM1XQcCBuael+a1qQcCBuael+a1qQMG9E4DBo4MBwIXMTjlkagv5pif5pyf5LiJLzUtN+iKggoDB2MHAhvniannkIbkuI7mnZDmlpnnp5HlrablrabpmaIHAhblpKflrabniannkIblrp7pqow25a6kCQMHAAkHAAcABv//AwYwEwcCOygxMTAyMTAwMDEp6L+I5YWL5bCU6YCK5bmy5raJ5Luq5rWL5YWJ5rOi55qE5rOi6ZW/WzPlrabml7ZdCQcCBuael+a1qQcCBuael+a1qQMG9E4DBpwMBwIYMTDlkagv5pif5pyf5LiALzktMTHoioIKAwdjBwIb54mp55CG5LiO5p2Q5paZ56eR5a2m5a2m6ZmiBwIX5aSn5a2m54mp55CG5a6e6aqMMTDlrqQJAwcBCQIFU3RhdGUHrgcSBwACAAcBAgEHAgIBBwMCAQcEAgEHBQIBBwYCAQcHAgEHCAIBBwkCAQcKAgEHCwIBBwwCAQcNAgEG//8CAAb//wIABv//AgAG//8CAAcEBwAHAQIAAAAAAIBBQAcBBwECAAAAAAAAVEAHCQcBAgAAAAAAAHlABwoHAQIAAAAAAEBgQAcABwAHAAIABzIDBhQTAgJJRAkCAAIBAwcEAgAHAAIBB1YHAAIBBwAHAAIIUGFnZVNpemUDBxkCCVBhZ2VJbmRleAMHAg==",
        "__CALLBACKID": "ctl00$ContentPlaceHolder1$ASPxCallbackPanel1$ASPxGridView1",
        "__CALLBACKPARAM": "c0:KV|176;['4576','4577','4638','4639','4654','4655','4662','4663','4666','4667','4668','4669','4670','4671','4688','4690','4692','4693','4711','4713','4716','4717','4719','4721','4756'];GB|20;12|PAGERONCLICK3|PN"+str(page)+";",
    }), encoding="utf-8")
    request_package = urllib.request.Request(url=des_url, headers=request_header, data=bytes(request_data), method="POST")
    response = urllib.request.urlopen(request_package).read().decode("utf-8")
    return response


# 处理数据
def analyzeData(html):
    index = 0
    project_list = []
    disposed_html = BeautifulSoup(html, "html.parser")
    for project_item in disposed_html.find_all("td", class_="gvCell dxgv"):
        str_project_item = str(project_item)
        project_info = re.findall(project_pattern, str_project_item)
        # 过滤空数组
        if project_info:
            project_list.append(project_info[0])
            index = index + 1
            # 每9个数据为一组
            if index % 9 == 0:
                project = {
                    "name": re.findall(re.compile("[\u4E00-\u9FA5]+"), project_list[2])[0],
                    "range": re.sub("<br/>", "", project_list[3]),
                    "teacher": project_list[4],
                    "time": re.sub("<br/>", "", project_list[5]),
                    "lab": project_list[6]
                }
                projects.append(project)
                project_list = []


# 初始化数据库
def initializeDatabase(database_save_path):
    database = sqlite3.connect(database_save_path)
    cursor = database.cursor()
    # 注意检查数据库是否存在
    sql_operation = """
        create table IF NOT EXISTS 广州大学实验数据
            (id INTEGER not null
                primary key autoincrement,
            name text not null,
            range text not null,
            teacher text not null,
            time text not null,
            lab text not null
            )
    """
    cursor.execute(sql_operation)
    database.commit()
    database.close()


# 保存数据
def saveAsDatabase(database_save_path):
    database = sqlite3.connect(database_save_path)
    cursor = database.cursor()
    for item in projects:
        sql_operation = """
            insert into 广州大学实验数据 (name, range, teacher, time, lab)
                values ("{0}", "{1}", "{2}", "{3}", "{4}")
        """.format(item["name"], item["range"], item["teacher"], item["time"], item["lab"])
        cursor.execute(sql_operation)
        database.commit()
    database.close()


if __name__ == "__main__":
    main()
