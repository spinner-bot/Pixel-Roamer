# Pixel Roamer 工作约定

- 开始工作前阅读 `specs/项目规范/版本管理规范.md`，始终遵守版本管理规范。
- 作者名按项目用户明确要求设置为 `Codex  (sqs_A100)`（Codex 后两个空格）；邮箱沿用 spinner-bot 对应的仓库邮箱。此明确要求优先于规范中的默认显示名。
- 每完成一个文件或模块即提交；通过 SSH 密集推送经过相关测试的修复。pull/merge 必须使用 `--no-ff`，不得强推覆盖协作者历史。
- 当前阶段集中系统性修复已有玩法和地图；新增玩法需要用户明确要求。
- 修复须有可重复测试；在 `docs/进展报告` 记录复现输入、修复前后证据、验证结果及仍未覆盖的边界，不把离屏测试称为实机验收。
- 运行 `python3 -m unittest discover -s tests -v`；持续模拟可使用 `scripts/audit_runtime.py`。原始审计数据存放在 `docs/进展报告/evidence`。
