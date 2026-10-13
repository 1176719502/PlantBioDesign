# 五项历史失败与实际验收范围

| 测试 | 既有语义/边界 |
|---|---|
| test_matching_bound_reference_and_provenance_are_visible | 期望 ALB，保存名为 ALB_cold_reopen_verified；来源绑定保留 |
| test_missing_source_stays_missing | 同一名称失配；缺失来源仍为 Not provided |
| test_role_only_history_is_not_current_source | 期望 NCBI RefSeq 前缀，保存值为 accession；历史/当前归属边界保留 |
| test_saved_source_projection_is_visible_in_both_formats | 期望扩展描述而 fixture 仅存 accession；首失败遮挡后续 PDF 断言，不能计为 pass |
| test_single_reference_conflicting_with_single_provenance_is_unconfirmed | 名称与 NCBI 前缀失配；冲突来源仍未确认 |

基线16项：11 passed/5 failed；整合与独立候选各80项：75 passed/5 failed；全新安装70个有效用例：65 passed/5 failed。失败集合及消息一致仅支持已比较范围内未发现本次新增失败，不证明任意未运行套件无回归，也不是全软件全绿。本轮不重跑这些实验。

验证只覆盖原报告指定 Windows x64 / CPython 3.12、案例、下载及保存/重开/正常停止后冷恢复；不代表全部宿主、Multi-TU、Pathway 或全部功能 GO。历史 ALB 完整流程 GO 只属于其固定提交/单案例，本轮不重跑 ALB。
