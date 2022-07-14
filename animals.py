import re

from common.slicer import slice_text, pack_sentence


class AnimalCommon:
    org_slices = {}
    tiny_slice_delimiter = ';；,，'

    def get_org_name(self, text):
        ret, name_regex = '', ''
        for name_regex, info in self.org_slices.items():
            result = re.match(name_regex, text)
            if result:
                ret = result[0]
                break

        return ret, name_regex

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

            text = text.lstrip('雌雄♀♂：:')

        com = re.compile(r'([\dO]\.[\dO])')
        regex = r'。' if com.search(text) else '.。'

        for paragraph in re.split(regex, text):
            name, regex = self.get_org_name(paragraph)
            if name:
                detail = paragraph.lstrip(name).lstrip(',，其的')
                cont_dict = self.handle_organ(detail, self.org_slices[regex])
                ret.update({name: cont_dict})
            else:
                ret.update(slice_text(paragraph))

        return {sex: ret} if sex else ret

    def handle_organ(self, organ_text, organ_list):
        ret = dict()
        sliced = re.split(r'[%s]' % self.tiny_slice_delimiter, organ_text)

        organ_list = set(organ_list)
        last_org = '形态'

        for item in sliced:
            item = item.lstrip('：:')
            if not item:
                continue

            for o in organ_list:
                if item.startswith(o):
                    last_org = o
                    break

            ret[f'{last_org}：{item.lstrip(last_org).lstrip(":：")}'] = {}

        return ret


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
              '梗节', '索节', '棒节', '微毛区', '端', '颅顶、颊', '颅顶', '颊', '第1鞭节', '第2鞭节', '第3鞭节', '颜面'],
        '胸': ['长', '前胸背板', '基节', '后胸', '中胸', '盾', '小盾片', '后胸背板', '基', '并胸腹节'],
        '足': ['跗爪', '后足腿节', '后足胫节', '后足跗节', '爪'],
        '腹': ['第1背板', '第2背板', '基区', '第3背板', '其余背板', '第2—3背板', '产卵管', '背脊', '背'],
        '变异': ['触角', '产卵管', '腹部', '其他']
    }

    @staticmethod
    def handle_chi(text):
        ret = dict()

        text = text.lstrip('翅')
        com = re.compile(r'[；;]')
        front_com = re.compile(r'([\u4e00-\u9fa5]+)')

        for item in com.split(text):
            mi = front_com.match(item)
            if mi and mi[1] != '前翅':
                info = pack_sentence(item)
                ret.update(info)
            else:
                ret[f'前翅：{item.lstrip("前翅：")}'] = {}

        return {'翅': ret} if ret else ret

    def my_slice(self, text):
        ret = dict()

        if text.startswith('翅'):
            ret.update(self.handle_chi(text))

        elif text.startswith('体色'):
            last_not_matched_key = ''
            color_info = dict()
            for item in re.split(r'[；;，。]', text):
                com = re.compile(r'(.*?)([深浅黄褐].*?色)')
                res = com.search(item)
                if res:
                    key, value = res[1].rstrip('：'), res[2]
                    color_info[f'{last_not_matched_key + key}：{value}'] = dict()
                    last_not_matched_key = ''
                else:
                    last_not_matched_key = last_not_matched_key + item

            ret['颜色'] = color_info

        else:
            org_name = ''
            for org in self.org_slices.keys():
                if text.startswith(org):
                    org_name = org
                    break

            if org_name:
                _, regex = self.get_org_name(org_name)
                ret[org_name] = dict()
                for item in re.split('。', text):
                    detail = item.lstrip(org_name).lstrip(',，其的')
                    cont_dict = self.handle_organ(detail, self.org_slices[regex])
                    ret[org_name].update(cont_dict)
            else:
                ret.update(self.slice(text))

        return ret


class Sou(AnimalCommon):
    org_slices = {
        '头部': ['头缝', '两侧', '后角', '后缘', '复眼', '触角', '基节', '第1节', '第2节', '第3节', '第4节', '第5节', '其余各节'],
        '前胸背板': ['前缘', '两侧', '后缘', '背面', '中沟', '后翅'],
        '前翅': ['肩角', '外缘', '内后角', '内、外后角', '表面'],
        '末腹': ['背板', '两侧', '后角', '后缘', '后部'],
        '尾铗': ['前部', '后部', '两支', '顶端', '内缘', '雌虫尾铗'],
        # '足': ['后足跗节'],
        # '阳茎': ['阳茎叶端', '阳茎端刺', '基囊'],
        '雌虫': ['末腹背板甚', '基部', '两尾铗', '后部', '顶端']
    }
    tiny_slice_delimiter = ';；'

    def my_slice(self, text):
        ret = dict()

        if text.startswith('体长'):
            for item in re.split(r'[；;]', text):
                ret[item] = {}
        else:
            ret.update(self.slice(text))

        return ret


class Ya(AnimalCommon):
    org_slices = {
        '玻片标本': ['头部、胸部', '头部', '胸部', '腹部', '节Ⅲ—Ⅵ', '喙、足', '喙', '足', '跗节', '腹管、尾片',
                 '腹管', '尾片', '触角', '其他'],
        '触角': ['节Ⅲ', '节Ⅰ—Ⅵ', '触角毛', '一般各节', '各节', '长毛', '原生感觉圈', '次生感觉圈'],
        '腹部': ['背片'],
        '体表': ['头', '腹部', '背片']
    }
    tiny_slice_delimiter = ';；,，'

    def my_slice(self, text):
        ret = dict()

        orgs = ['观察标本']
        for item in re.split(r'。', text):
            flag = False
            for org in orgs:
                if not item.startswith(org):
                    continue
                item = item.lstrip(org).lstrip('：:')
                info = dict()
                for k in re.split(r'[;；。]', item):
                    info[f'{org}：{k}'] = {}
                ret[org] = info
                flag = True
                break

            if not flag:
                ret.update(self.slice(item))

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
        ret.update(Feng().my_slice(text))

    elif keyword.endswith('螋'):
        ret.update(Sou().my_slice(text))

    elif '蚜' in keyword:
        ret.update(Ya().my_slice(text))

    return ret
