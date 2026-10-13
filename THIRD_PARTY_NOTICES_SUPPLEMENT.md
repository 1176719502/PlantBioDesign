# V1.0 source release — third-party notice supplement

PlantBioDesign V1.0 维护版源码已于2026-10-13更新到公开 main，正式提交为 [`6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b`](https://github.com/1176719502/PlantBioDesign/commit/6c7169a4c95d0b74a8b73bfb111ed7056a3eb99b)；该提交包含已经批准的715文件源码版本。本次维护版没有创建 GitHub Release，没有创建 v1.0.1 标签，也没有单独上传供下载的 ZIP Release 资产。仓库已有的论文历史快照 Release 不属于本次维护版发布。 本补充不是完整运行时合规证明。

历史上游原始源码候选为 `V1_0_PUBLIC_RELEASE_CANDIDATE_R1_SOURCE.zip`（706 文件），ZIP SHA-256：`49A40ECB2AA4B40F6879B431F26789D488405E1C9B0BDC18E875786FC85D8D67`。旧715文件准备包为 `V1_0_PUBLIC_RELEASE_PREPARATION_SOURCE_CORRECTION_R1.zip`，ZIP SHA-256：`AB3C8A3ACE759E2D55B1A1004DA0038573ABA620A93C9E1997756F4FE7722A6C`；它在706文件候选上仅修改入口 README 并增加9份说明/许可文件，没有改变生产代码、锁或序列。最终获批准的715文件包为 `V1_0_PUBLIC_RELEASE_WHITESPACE_CORRECTED_R1.zip`，ZIP SHA-256：`06F3228293DCCFD21158316DEF4C408237EB1FCC57FB0AD394A3B96EE608AAA2`；相对旧715包仅删除 README 末尾一组 CRLF（2字节），其余714文件同字节。上述 ZIP SHA-256 均不是 Git commit SHA。原 ZIP 及包外校验/资产文件未随本次 main 更新上传；GitHub 自动源码归档不是原批准 ZIP，不能使用该 ZIP SHA-256 校验自动归档。本次文档修正不重建或覆盖这些历史 ZIP。 历史清单49项未覆盖当前锁52项，以下三项补充不改写历史清单审查状态。

| Package | Locked version | Exact-version license basis | Distribution scope |
|---|---|---|---|
| pypdf | 6.10.0 | BSD-3-Clause | 新增依赖声明；程序本体未随本源码包分发 |
| ReportLab | 4.2.2 | BSD three-clause-style LICENSE | 既有依赖；程序本体未随本源码包分发 |
| chardet | 7.6.0 | 0BSD | 既有依赖；本版本不可套用其他版本的历史许可 |

以下原文来自已按锁安装的相应 dist-info LICENSE，保留原文版权年份及条件。ReportLab 的 LICENSE 记2000–2018，METADATA记2000–2022；本补充不擅自统一年份。用户安装或再分发依赖时须遵守对应精确版本及其嵌套组件条款。源码包随附字体的 OFL、版权和 provenance 仍适用，项目 MIT 不取代它们。

## chardet 7.6.0

原始许可文件 SHA-256：`0517F574B0183D991EB7A9EC5DBF0ADD8D8ADE5AC00341BD28CA0C18914D52E5`

```text
Copyright (c) 2026 Dan Blanchard



Permission to use, copy, modify, and/or distribute this software for any

purpose with or without fee is hereby granted.



THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH

REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND

FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,

INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS

OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER

TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF

THIS SOFTWARE.
```

## pypdf 6.10.0

原始许可文件 SHA-256：`A97AC230E5F33EF10A5367A850EB01F91F1A0B064E34742C7794D2294557F524`

```text
Copyright (c) 2006-2008, Mathieu Fenniak
Some contributions copyright (c) 2007, Ashish Kulkarni <kulkarni.ashish@gmail.com>
Some contributions copyright (c) 2014, Steve Witham <switham_github@mac-guyver.com>

All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

* Redistributions of source code must retain the above copyright notice,
this list of conditions and the following disclaimer.
* Redistributions in binary form must reproduce the above copyright notice,
this list of conditions and the following disclaimer in the documentation
and/or other materials provided with the distribution.
* The name of the author may not be used to endorse or promote products
derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
POSSIBILITY OF SUCH DAMAGE.
```

## reportlab 4.2.2

原始许可文件 SHA-256：`A02A6AEB5DDE4C4194494BC0B10D5ED62A32628CCD2882C363FDB9A7874AB2B8`

```text
#####################################################################################
#
#	Copyright (c) 2000-2018, ReportLab Inc.
#	All rights reserved.
#
#	Redistribution and use in source and binary forms, with or without modification,
#	are permitted provided that the following conditions are met:
#
#		*	Redistributions of source code must retain the above copyright notice,
#			this list of conditions and the following disclaimer. 
#		*	Redistributions in binary form must reproduce the above copyright notice,
#			this list of conditions and the following disclaimer in the documentation
#			and/or other materials provided with the distribution. 
#		*	Neither the name of the company nor the names of its contributors may be
#			used to endorse or promote products derived from this software without
#			specific prior written permission. 
#
#	THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#	ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#	WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED.
#	IN NO EVENT SHALL THE OFFICERS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#	INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#	TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#	OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
#	IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING
#	IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
#	SUCH DAMAGE.
#
#####################################################################################
```


实际分发义务若必须履行但未满足，立即标记为发布阻塞，不能仅靠免责声明替代。完整源码包仍保留原 MIT/OFL/字体 provenance/序列来源说明；本补充不改写历史49项表为52项。本公开源码副本附原字节许可：[release-notices/](release-notices/)。旧包外发布材料中的 licenses/ 不属于本公开源码树。
