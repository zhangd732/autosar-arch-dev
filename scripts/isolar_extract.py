# -*- coding: utf-8 -*-
"""
isolar_extract.py — Phase 5.5a：ECU 抽取（headless）调用与核验脚本
====================================================================

项目：N80KS VIUMR，AUTOSAR Classic Platform，ETAS ISOLAR-AB 12.4.0。
封装 `ISOLAR-A.cmd -ecuextract`，完成：前置校验 → 组装命令 → 调用 →
三层成功判定 → 产物核验 → JSON 结构化结果输出。

用法：
    python isolar_extract.py --project="D:\\Proj\\X"
    python isolar_extract.py --project="D:\\Proj\\X" --discover   # 仅扫描 ShortName
    python isolar_extract.py --help

Gate A 判断标准（是否应运行本脚本）见 SKILL.md "Phase 5.5" 章节。
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
DEFAULT_PROJECT = r""          # TODO【可选】: 填入常用项目根目录，留空则必须用 --project 指定
DEFAULT_ECU = "VIU_MR"         # EcuInstance ShortName（旁证：VIU_MR_FlatView_SWCD.arxml）
DEFAULT_SYSTEM = "System"      # System ShortName（旁证：BasicSoftware/System_EcuExtr.arxml）

# --otheropt 偏好文件：默认用 skill 内置模板（assets/EcuExtract_CLI_Input.txt，源自 ISOLAR-AB 12.4.0 官方样例）
# 相对脚本位置解析，skill 目录整体移动后仍有效；也可用 --otheropt 参数覆盖
DEFAULT_OTHEROPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "EcuExtract_CLI_Input.txt")

# 成功日志字样（三层判定第②层）
SUCCESS_LOG_PATTERN = "EcuExtract is generated successfully"


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


def discover_shortnames(project):
    """
    --discover 模式：正则扫描项目内全部 *.arxml，
    提取 <ECU-INSTANCE> / <SYSTEM> 元素块下的第一个 <SHORT-NAME>。
    """
    ecu_names, sys_names = set(), set()
    pat_ecu = re.compile(
        r"<ECU-INSTANCE\b[^>]*>.*?<SHORT-NAME>([^<]+)</SHORT-NAME>", re.S)
    pat_sys = re.compile(
        r"<SYSTEM\b[^>]*>.*?<SHORT-NAME>([^<]+)</SHORT-NAME>", re.S)
    for root, _dirs, files in os.walk(project):
        for fn in files:
            if not fn.lower().endswith(".arxml"):
                continue
            fp = os.path.join(root, fn)
            try:
                with open(fp, "r", encoding="utf-8", errors="ignore") as f:
                    text = f.read()
            except OSError:
                continue
            for m in pat_ecu.finditer(text):
                ecu_names.add(m.group(1).strip())
            for m in pat_sys.finditer(text):
                sys_names.add(m.group(1).strip())
    return sorted(ecu_names), sorted(sys_names)


def ulf_has_error(ulf_path):
    """三层判定第③层：ULF 中是否存在 <CATEGORY>ERROR</CATEGORY> 条目。"""
    if not ulf_path or not os.path.isfile(ulf_path):
        return False, 0
    with open(ulf_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    errors = re.findall(r"<CATEGORY>\s*ERROR\s*</CATEGORY>", text, re.I)
    return (len(errors) > 0), len(errors)


def log_has_success(log_path):
    """三层判定第②层：日志中是否出现成功字样。"""
    if not log_path or not os.path.isfile(log_path):
        return False
    with open(log_path, "r", encoding="utf-8", errors="ignore") as f:
        text = f.read()
    return SUCCESS_LOG_PATTERN in text


def find_artifact(project, filename):
    """在 project 下递归查找指定文件名，返回完整路径或 None。"""
    for root, _dirs, files in os.walk(project):
        if filename in files:
            return os.path.join(root, filename)
    return None


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser(
        description=u"Phase 5.5a：ECU 抽取（headless ecuextract）调用与核验")
    ap.add_argument("--project", default=DEFAULT_PROJECT,
                    help=u"项目文件夹路径（含 .project），必填")
    ap.add_argument("--ecu", default=DEFAULT_ECU,
                    help=u"EcuInstance ShortName（默认 %(default)s）")
    ap.add_argument("--system", default=DEFAULT_SYSTEM,
                    help=u"System ShortName（默认 %(default)s）")
    ap.add_argument("--otheropt", default=DEFAULT_OTHEROPT,
                    help=u"偏好文件 EcuExtract_CLI_Input.txt 路径（可选）")
    ap.add_argument("--log", default="",
                    help=u"日志输出路径（缺省：<project>/_logs/ecuextract.log）")
    ap.add_argument("--ulf", default="",
                    help=u"ULF XML 错误报告路径（缺省：<project>/_logs/ecuextract.ulf）")
    ap.add_argument("--discover", action="store_true",
                    help=u"仅扫描项目 arxml，列出 ECU-INSTANCE / SYSTEM 候选 ShortName，不执行抽取")
    args = ap.parse_args()

    if not args.project:
        die(u"必须用 --project 指定项目文件夹路径（或在配置区填 DEFAULT_PROJECT）。")
    project = os.path.abspath(args.project)
    if not os.path.isdir(project):
        die(u"项目目录不存在：%s" % project)

    # --discover 模式：只扫描 ShortName，不需要 ISOLAR_A_CMD
    if args.discover:
        ecu_names, sys_names = discover_shortnames(project)
        print(u"[discover] ECU-INSTANCE 候选 ShortName：")
        for n in ecu_names:
            print(u"  - %s" % n)
        print(u"[discover] SYSTEM 候选 ShortName：")
        for n in sys_names:
            print(u"  - %s" % n)
        print(u"[discover] 请人工确认后回填脚本配置区 DEFAULT_ECU / DEFAULT_SYSTEM。")
        sys.exit(0)

    check_isolar_cmd(ISOLAR_A_CMD)

    # 缺省日志/ULF 路径
    log_dir = os.path.join(project, "_logs")
    log_path = args.log or os.path.join(log_dir, "ecuextract.log")
    ulf_path = args.ulf or os.path.join(log_dir, "ecuextract.ulf")
    for p in (log_path, ulf_path):
        d = os.path.dirname(os.path.abspath(p))
        if d and not os.path.isdir(d):
            os.makedirs(d)

    # 组装命令
    cmd = [ISOLAR_A_CMD, "-ecuextract",
           '--project="%s"' % project,
           "-e=%s" % args.ecu,
           "-s=%s" % args.system,
           '--log="%s"' % log_path,
           '--ulf="%s"' % ulf_path]
    if args.otheropt:
        if not os.path.isfile(args.otheropt):
            die(u"偏好文件不存在：%s" % args.otheropt)
        cmd.append('--otheropt="%s"' % args.otheropt)

    print(u"[执行] %s" % " ".join(cmd))

    # subprocess 调用（.cmd 需要 shell=True）
    proc = subprocess.run(" ".join(cmd), shell=True,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    exit_code = proc.returncode

    # 三层成功判定
    layer1_ok = (exit_code == 0)
    layer2_ok = log_has_success(log_path)
    layer3_has_err, ulf_err_cnt = ulf_has_error(ulf_path)
    layer3_ok = not layer3_has_err

    # 产物核验：递归找 3 个产物 arxml
    artifacts = {
        "flatmap": u"%s_FlatMap.arxml" % args.ecu,
        "flatview_swcd": u"%s_FlatView_SWCD.arxml" % args.ecu,
        "ecuextr": u"%s_EcuExtr.arxml" % args.system,
    }
    artifact_result = {}
    for key, fname in artifacts.items():
        found = find_artifact(project, fname)
        artifact_result[key] = {"file": fname, "found": bool(found),
                                "path": found or ""}
    artifacts_ok = all(v["found"] for v in artifact_result.values())

    overall = layer1_ok and layer2_ok and layer3_ok and artifacts_ok

    result = {
        "phase": "5.5a-ecuextract",
        "command": " ".join(cmd),
        "checks": {
            "exit_code": {"value": exit_code, "ok": layer1_ok},
            "log_success": {"pattern": SUCCESS_LOG_PATTERN, "ok": layer2_ok,
                            "log": log_path},
            "ulf_no_error": {"error_count": ulf_err_cnt, "ok": layer3_ok,
                             "ulf": ulf_path},
            "artifacts": {"ok": artifacts_ok, "detail": artifact_result},
        },
        "overall": "PASS" if overall else "FAIL",
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))

    if overall:
        print(u"[结果] Phase 5.5a 核验通过。请汇报用户，获得许可后进入 Phase 5.5b。")
        sys.exit(0)
    else:
        print(u"[结果] Phase 5.5a 核验未通过，请按上方 checks 逐项排查，勿进入后续工序。")
        sys.exit(1)


if __name__ == "__main__":
    main()
