import re

from common.slicer import slice_text, slice_organs


class AnimalCommon:
    org_slices = {}

    def get_org_name(self, text):
        ret, name_regex = '', ''
        for name_regex, info in self.org_slices.items():
            result = re.match(name_regex, text)
            if result:
                ret = result[0]
                break

        return ret, name_regex

    @staticmethod
    def pack_sample(text):
        ret = dict()

        for item in re.split(r'；;', text):
            ret[f'标本：{item}'] = {}

        return ret

    def slice(self, text):
        ret = dict()

        sex = ''
        com = re.compile(r'([雌雄♀♂]性?)')
        info = com.match(text)
        if info:
            sex = info[0]
            if sex == '♂':
                sex = '雄'
            elif sex == '♀':
                sex = '雌'

            text = text.lstrip('雌雄性♀♂：:')

        for paragraph in re.split(r'。', text):
            if text.startswith('标本记录'):
                ret.update(self.pack_sample(paragraph))
                continue

            name, regex = self.get_org_name(paragraph)
            if name:
                detail = paragraph.lstrip(name).lstrip(',，其的：')
                cont_dict = slice_organs(detail, self.org_slices[regex])
                if name not in ret:
                    ret[name] = cont_dict
                else:
                    ret[name].update(cont_dict)
            else:
                ret.update(slice_text(paragraph))

        return {sex: ret} if sex else ret


class MiXia(AnimalCommon):
    org_slices = {
        '额角': ['末端', '上缘', '基部', '下缘'],
        '头胸甲': ['长度', '前侧'],
        '尾节': ['背面', '末端', '末缘', '中央', '背侧', '末端'],
        # '侧刺': [],
        '间刺': ['中央间刺', '外侧间刺'],
        '柄刺': [],
        '肛前脊': [],
        r'(第\d触角)': ['柄刺', '第1节', '第2节', '第3节', '鳞片', '内肢'],
        r'(第\d颚足)': ['末节', '顶端', '末节', '约等于', '内肢', '末端', '末2节'],
        r'(第\d步足)': ['长节', '腕节', '螯', '螫', '掌节', '掌', '指节', '座节', '前缘', '腹缘', '末端', '长'],
        r'(第\d腹肢)': ['内肢', '内缘', '长', '基部', '末端', '末部', '内肢', '内附肢'],
        # '尾肢': [],
        '卵': ['卵径']
    }


class ZhiHuanChong(AnimalCommon):
    org_slices = {
        '成虫': ['虫体', '体长', '体宽', '长', '宽', '全长'],
        '咽': ['大小'],
        '后吸器': ['边缘', '柄', '钩尖', '小钩', '长'],
        '中央大钩': ['交接管', '基部', '交接器', '边缘', '钩尖', '全长', '外突', '内突'],
        '边缘': ['小钩', '长', '全长'],
        '联结片': ['中部', '两端', '副联结片', '大小'],
        '副联结片': ['大小'],
        '支持器': ['外缘', '凹面', '中部', '薄片', '柄端', '基部', '前端', '棒片', '交接管', '全长', '基端', '端部', '长', '叉', '一叉'],
        '交接管': ['基径', '管径', '管长', '端部', '基部', '支持器', '外缘', '凹面', '中部', '薄片', '长', '基端'],
        '阴道': ['管', '末端', '管长', '直径', '泡状部分', '泡状', '长', '盘圈'],
        "卵子": ['卵', '长', '宽', '具']
    }


class Luo:
    @staticmethod
    def slice(text):
        ret = dict()

        if text.startswith('壳高'):
            com = re.compile(r'([\u4e00-\u9fa5]*)(\d*[.。．]*\d*[a-zA-Z]*)')
            for item in com.findall(text):
                if item[0] and item[1]:
                    ret[f'{item[0]}：{item[1]}'] = {}

        return {'标本测量：': ret} if ret else ret


class Feng(AnimalCommon):
    org_slices = {
        '头': ['触角', '柄节', '上颊', '后头', '头顶', '脸', '蠢基', '唇基', '口窝', '颊', '颚眼', '近后头脊', '近复眼', '顶',
              '微毛区', '端', '颅顶', '颊', '颜面', 'POL', '下脸', '中胸盾片', '复眼', '上颚', '上唇'],
        '翅': ['缘室', 'r脉', 'SR1+3-SR脉', 'SR1+3-SR脉', '2-SR脉', 'cu-a脉', 'M+CU脉', '前翅SR1脉', '2-M脉', 'CH-a脉', '前翅', '翅痣',
              '1-R1脉'],
        '胸': ['长', '前胸背板', '基节', '后胸', '中胸', '盾', '小盾片', '后胸背板', '基', '并胸腹节'],
        '足': ['跗爪', '后足腿节', '后足胫节', '后足跗节', '爪', '基跗节', '基节', '前后足腿节', '转节', '前后足腿节', '中足', '前后足'],
        '腹': ['第1背板', '第2背板', '基区', '第3背板', '第4背板', '其余背板', '第2—3背板', '产卵管', '背脊',
              '背', '气门', '背板', '下生殖板', '鞘', '产卵管', '柄', '前部', '两侧', '第1-2背板及第3背板基半', '产卵管鞘'],
        '变异': ['触角', '产卵管', '腹部', '其他'],
        '触角': ['梗节', '索节', '棒节', '柄节', '第1鞭节', '第2鞭节', '第3鞭节', '上端', '第一索节', '第二索节',
               '腹部第2-6节', '第1—3节', '第4—6节', '第7节', '第6腹板', '生殖刺突']
    }

    def my_slice(self, text):
        ret = dict()

        for para in re.split('。', text):
            com = re.compile(r'(.*?)([深浅黄褐黑锈].*?色)[，；。]')

            color_info = dict()
            for item in com.findall(para):
                color_info[f'{item[0]}：{item[1]}'] = {}

            if color_info:
                ret.update(color_info)
            else:
                ret.update(self.slice(para))

        return ret


class Sou(AnimalCommon):
    org_slices = {
        '头部': ['头缝', '两侧', '后角', '后缘', '复眼', '触角', '基节', '第1节', '第2节', '第3节', '第4节', '第5节', '其余各节'],
        '前胸背板': ['前缘', '两侧', '后缘', '背面', '中沟', '后翅'],
        '前翅': ['肩角', '外缘', '内后角', '内、外后角', '表面'],
        '腹部': ['雄虫两侧', '后缘', '后部', '末腹'],
        '末腹': ['背板', '两侧', '后角', '后缘', '后部'],
        '尾铗': ['前部', '后部', '两支', '顶端', '内缘', '雌虫尾铗', '基部'],
        '亚末腹': ['板', '后缘', '表面'],
        '足': ['后足跗节', '腿节', '腹面'],
        '臀板': ['基部', '两侧', '后外侧', '后缘', '两后角'],
        '阳茎': ['阳茎叶端', '阳茎端刺', '基囊'],
        '鞘翅': ['前翅', '后缘', '后内角', '后翅', '外缘'],
        '触角': ['基节', '第2节', '第3节', '第4节', '其余各节'],
        '雌虫': ['末腹背板甚', '基部', '两尾铗', '后部', '顶端']
    }

    def my_slice(self, text):
        ret = dict()

        for item in re.split(r'。', text):
            if item.startswith('体长'):
                for p in re.split(r'[；;]', item):
                    ret[p] = {}
            else:
                ret.update(self.slice(item))

        return ret


class Ya(AnimalCommon):
    org_slices = {
        '玻片标本': ['头部、胸部', '头部', '胸部', '腹部', '喙、足', '喙', '足', '跗节', '腹管、尾片',
                 '腹管', '尾片', '触角', '其他', '中、后胸', '腹'],
        '触角': ['触角毛', '一般各节', '各节', '长毛', '原生感觉圈', '次生感觉圈', '基部'],
        '腹部': ['背片'],
        '体表': ['头', '腹部', '背片']
    }

    def my_slice(self, text):
        ret = dict()
        com = re.compile(r'([有无]翅孤雌蚜)：?(.*)')

        for item in com.findall(text):
            ret.update({item[0].rstrip('：'): self.slice(item[1])})

        return ret


class Jie(AnimalCommon):
    org_slices = {
        '触角': [],
        '刺孔群': []
    }


class Chun(AnimalCommon):
    org_slices = {
        '体': ['体色', '毛', '臭腺'],
        '前胸背板': ['胝', '亚后缘', '后缘', '刻点', '毛'],
        '头': ['头宽', '长', '头顶'],
        '触角': ['第Ⅰ节', '雄虫', '雌'],
        '前翅': [],
        '膜片': [],
        '革片': [],
        '足': ['股节', '胫节', '后足', '基节', '前、中足', '各足胫节'],
        r'[左右]阳基': ['侧突', '端突', '端部', '基部', '近端部'],
        '阳茎': ['鞘', '端针'],
        '唇基': []
    }

    def my_slice(self, text):

        ret = dict()
        data = re.match(r'(量度\(?m{0,2}\)?)', text)
        if data:
            org_list = ['体长', '体宽', '头长', '头顶', '触角各节长', '后缘宽', '革片长', '楔片长', '前胸背板', '头宽']
            ret[data[0]] = slice_organs(text.replace(data[0], '').lstrip('：'), org_list)
        else:
            ret.update(self.slice(text))

        return ret


def slice_text_by_animal_org(keyword, text):
    ret = dict()

    if '米虾' in keyword:
        ret.update(MiXia().slice(text))

    elif '指环虫' in keyword or '三代虫' in keyword:
        ret.update(ZhiHuanChong().slice(text))

    elif keyword.endswith('螺'):
        ret.update(Luo().slice(text))

    elif keyword.endswith('蜂'):
        ret.update(Feng().slice(text))

    elif keyword.endswith('螋'):
        ret.update(Sou().my_slice(text))

    elif '蚜' in keyword:
        ret.update(Ya().my_slice(text))

    elif '蚧' in keyword:
        ret.update(Jie().slice(text))

    elif '蝽' in keyword:
        ret.update(Chun().my_slice(text))

    return ret
