# -*- coding: utf-8 -*-
"""
isolar_enablerips.py — Phase 5.5b：CSXfrm 使能（headless）调用与核验脚本
=========================================================================

项目：N80KS VIUMR，AUTOSAR Classic Platform，ETAS ISOLAR-AB 12.4.0。
封装 `ISOLAR-A.cmd -enablerips -t=CS_XFRM`，给 FlatMap 中目标 FID 写入
RTE-PLUGIN-PROPS，RTE 生成时据此挂接 C/S 数据变换插件。

用法：
    python isolar_enablerips.py --project="D:\\Proj\\X" --flatmap=VIU_MR_FlatMap
    python isolar_enablerips.py --help

Gate B 判断标准（是否应运行本脚本）见 SKILL.md "Phase 5.5" 章节。
前提：C/S 端口 FID 参与 Inter-ECU 通信且映射 Signal 配了 Data Transformation。
"""

import argparse
import json
import os
import re
import subprocess
import sys

# ---------------------------------------------------------------------------
# 配置区（使用前必须填写）
# ---------------------------------------------------------------------------

# TODO【用户必填】: 填入本机 ISOLAR-A.cmd 的完整路径，例如：
#   ISOLAR_A_CMD = r"C:\ETAS\ISOLAR-AB-12.4\ISOLAR-A.cmd"
# 也可用环境变量 ISOLAR_A_CMD 临时覆盖（测试/多版本切换场景）。
ISOLAR_A_CMD = os.environ.get("ISOLAR_A_CMD", r"E:\tools\ETAS\ISOLAR-AB_12.4.0\ISOLAR-A.cmd")

# 项目默认值（N80KS VIUMR，可用 CLI 参数覆盖）
DEFAULT_PROJECT = r""                    # TODO【可选】: 常用项目根目录
DEFAULT_FLATMAP = "VIU_MR_FlatMap"       # FlatMap ShortName
DEFAULT_TYPE = "CS_XFRM"                 # 本工序固定 CS_XFRM

# enablerips 允许的类型集合
ALLOWED_TYPES = ("SR_COM", "IMPL_TIMED_COM", "CS_XFRM",
                 "CS_SAFETY", "SIG_2_SRV", "ALL")

# 日志中的"无可用 FID"提示（不按硬失败处理）
NO_FID_HINT = "No possible FlatInstanceDescriptors"


# ---------------------------------------------------------------------------
# 工具函数
# ---------------------------------------------------------------------------

def die(msg, code=2):
    """打印错误并以非零码退出。"""
    print(u"[错误] %s" % msg)
    sys.exit(code)


def check_isolar_cmd(path):
    """前置校验：ISOLAR_A_CMD 已配置且文件存在。"""
    if not path or path.startswith("<TODO"):
        die(u"ISOLAR_A_CMD 未配置。请编辑本脚本顶部配置区，填入 ISOLAR-A.cmd 完整路径。")
    if not os.path.isfile(path):
        die(u"ISOLAR-A.cmd 不存在：%s" % path)


def find_artifact(project, filename):
    """在 project 下递归查找指定文件名，返回完整路径或 None。"""
    for root, _dirs, files in os.walk(project):
        if filename in files:
            return os.path.join(root, filename)
    return None


def count_rte_plugin_props(filepath):
    """统计文件中 RTE-PLUGIN-PROPS 出现次数；文件不存在返回 -1。"""
    if not filepath or not os.path.isfile(filepath):
        return -1
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return len(re.findall(r"RTE-PLUGIN-PROPS", text))


def ulf_has_error(ulf_path):
    """三层判定第③层：ULF 中是否存在 <CATEGORY>ERROR</CATEGORY> 条目。"""
    if not ulf_path or not os.path.isfile(ulf_path):
        return False, 0
    with open(ulf_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    errors = re.findall(r"<CATEGORY>\s*ERROR\s*</CATEGORY>", text, re.I)
    return (len(errors) > 0), len(errors)


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=u"Phase 5.5b：CSXfrm 使能（headless enablerips）调用与核验")
    ap.add_argument("--project", default=DEFAULT_PROJECT,
                    help=u"项目文件夹路径（含 .project），必填")
    ap.add_argument("--flatmap", default=DEFAULT_FLATMAP,
                    help=u"目标 FlatMap ShortName（默认 %(default)s）")
    ap.add_argument("--type", default=DEFAULT_TYPE, choices=ALLOWED_TYPES,
                    help=u"使能类型（默认 %(default)s）")
    ap.add_argument("--fids", default="",
                    help=u"目标 FID 列表/正则（如 [DEP_[A-Z_a-z_0-9]*]）；省略则自动使能全部符合条件的 FID")
    ap.add_argument("--skipfids", default="",
                    help=u"要排除的 FID（与 --fids 同语法）")
    ap.add_argument("--splitfile", default="",
                    help=u"将 RtePluginProps 拆到独立 arxml；缺省原位写入 FlatMap 文件")
    ap.add_argument("--log", default="",
                    help=u"日志输出路径（缺省：<project>/_logs/enablerips.log）")
    ap.add_argument("--ulf", default="",
                    help=u"ULF XML 错误报告路径（缺省：<project>/_logs/enablerips.ulf）")
    args = ap.parse_args()

    if not args.project:
        die(u"必须用 --project 指定项目文件夹路径（或在配置区填 DEFAULT_PROJECT）。")
    project = os.path.abspath(args.project)
    if not os.path.isdir(project):
        die(u"项目目录不存在：%s" % project)

    check_isolar_cmd(ISOLAR_A_CMD)

    # 前置校验：FlatMap arxml 存在
    flatmap_file = find_artifact(project, u"%s.arxml" % args.flatmap)
    if not flatmap_file:
        die(u"未在项目下找到 FlatMap 文件：%s.arxml（应先执行 Phase 5.5a 生成）" % args.flatmap)
    print(u"[前置校验] FlatMap 文件：%s" % flatmap_file)

    # splitfile 目标路径（相对路径则落到 project 下）
    split_path = u""
    if args.splitfile:
        split_path = args.splitfile
        if not os.path.isabs(split_path):
            split_path = os.path.join(project, split_path)

    # 缺省日志/ULF 路径
    log_dir = os.path.join(project, "_logs")
    log_path = args.log or os.path.join(log_dir, "enablerips.log")
    ulf_path = args.ulf or os.path.join(log_dir, "enablerips.ulf")
    for p in (log_path, ulf_path):
        d = os.path.dirname(os.path.abspath(p))
        if d and not os.path.isdir(d):
            os.makedirs(d)

    # 核验基线：调用前统计 RTE-PLUGIN-PROPS 数量
    verify_target = split_path or flatmap_file
    props_before = count_rte_plugin_props(verify_target)

    # 组装命令
    cmd = [ISOLAR_A_CMD, "-enablerips",
           '--project="%s"' % project,
           '--flatmap="%s"' % args.flatmap,
           "-t=%s" % args.type,
           '--log="%s"' % log_path,
           '--ulf="%s"' % ulf_path]
    if args.fids:
        cmd.append('--fids=%s' % args.fids)
    if args.skipfids:
        cmd.append('--skipfids=%s' % args.skipfids)
    if split_path:
        cmd.append('--splitfile="%s"' % split_path)

    print(u"[执行] %s" % " ".join(cmd))

    # subprocess 调用（.cmd 需要 shell=True）
    proc = subprocess.run(" ".join(cmd), shell=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    exit_code = proc.returncode

    # 日志分析：成功判定 + "No possible FlatInstanceDescriptors" 识别
    log_text = u""
    if os.path.isfile(log_path):
        with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
            log_text = f.read()
    no_fid_hint = NO_FID_HINT in log_text

    # 三层判定（enablerips 无固定成功字样，第②层为日志存在且可读取）
    layer1_ok = (exit_code == 0)
    layer2_ok = bool(log_text)  # 日志非空视为工具正常跑完
    layer3_has_err, ulf_err_cnt = ulf_has_error(ulf_path)
    layer3_ok = not layer3_has_err

    # 事后核验：确认目标文件中 RTE-PLUGIN-PROPS 存在（且数量增加）
    props_after = count_rte_plugin_props(verify_target)
    props_increased = (props_before >= 0 and props_after > props_before)
    props_exist = (props_after > 0)
    # 核验粒度说明：无法精确匹配目标 FID 时，至少确认存在且数量增加
    if props_increased:
        verify_note = u"RTE-PLUGIN-PROPS 数量增加（%d → %d），核验通过" % (
            props_before, props_after)
        verify_ok = True
    elif no_fid_hint:
        verify_note = (u"日志报 '%s'：前提不满足或 FID 已全部使能，"
                       u"不按硬失败处理，请人工检查映射") % NO_FID_HINT
        verify_ok = True  # 特殊提示，不算失败
    elif props_exist:
        verify_note = (u"文件中已存在 RTE-PLUGIN-PROPS（%d 处），但本次未见新增；"
                       u"核验粒度受限（未精确匹配目标 FID），请人工确认") % props_after
        verify_ok = True
    else:
        verify_note = u"未在 %s 中找到 RTE-PLUGIN-PROPS，核验失败" % verify_target
        verify_ok = False

    overall = layer1_ok and layer2_ok and layer3_ok and verify_ok

    result = {
        "phase": "5.5b-enablerips",
        "command": " ".join(cmd),
        "checks": {
            "exit_code": {"value": exit_code, "ok": layer1_ok},
            "log_readable": {"ok": layer2_ok, "log": log_path},
            "ulf_no_error": {"error_count": ulf_err_cnt, "ok": layer3_ok,
                             "ulf": ulf_path},
            "no_fid_hint": {"detected": no_fid_hint, "pattern": NO_FID_HINT},
            "rte_plugin_props": {
                "ok": verify_ok,
                "file": verify_target,
                "before": props_before,
                "after": props_after,
                "note": verify_note,
            },
        },
        "overall": "PASS" if overall else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if no_fid_hint:
        print(u"[提示] %s —— 前提不满足（无跨 ECU C/S 或未配 Transformation）"
              u"或已全部使能；不算错误，请回报人工检查映射。" % NO_FID_HINT)

    if overall:
        print(u"[结果] Phase 5.5b 核验通过。请汇报用户，获得许可后进入 Phase 6。")
        sys.exit(0)
    else:
        print(u"[结果] Phase 5.5b 核验未通过，请按上方 checks 逐项排查，勿进入 Phase 6。")
        sys.exit(1)


if __name__ == "__main__":
    main()
