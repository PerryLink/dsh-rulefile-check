/**
 * dsh-rulefile-check — table shape and material contract.
 *
 * The plugin is data-only: this file declares which columns the material may use
 * and how they map onto canonical field names; the shared kit supplies the reader
 * and the check engine, and the rule pack declares every check. Adding a check
 * that fits an existing kind is a rule-pack edit, not a code change.
 */

import { canonicaliseRow, parseTable, type TableSpec } from './shared/table.ts'
import { runTableCheck, type TableCheckOptions, type TableInput } from './shared/rows.ts'
import type { Ruleset } from './shared/rules.ts'

/** Tool id exposed to the model, and the row id in `cordis.patch.yml`. */
export const TOOL_NAME = 'rulefile_check'

/** The register's column aliases, declared once so both the spec and the guard see them. */
const COLUMNS = {
  ruleId: ['规则编号', '规则ID', 'id', 'ruleId'],
  title: ['规则标题', '标题', 'title'],
  severity: ['定级', '严重度', 'severity', '级别'],
  basisKind: ['依据类型', 'basis.kind', 'kind', '依据状态'],
  document: ['依据文件', '文件名称', 'document'],
  clause: ['条款号', '条号', 'clause'],
  excerpt: ['摘录', 'excerpt', '原文摘录'],
  source: ['来源链接', '来源', 'source', '出处链接'],
  checkKind: ['检查类型', 'check.kind', 'kind'],
  params: ['参数', 'params', '检查参数'],
  disabled: ['是否停用', '停用', 'disabled'],
  note: ['备注', '说明', 'note', 'remark'],
} as const

/** How the material declares its table. */
export const SPEC: TableSpec = {
  rowKeys: ['rows', 'rules', 'items', '规则'],
  columns: COLUMNS,
  header: {
  packName: ['packName', '规则库名称', '文件名'],
  plugin: ['plugin', '插件名', '适用插件'],
  version: ['version', '规则库版本', '版本'],
  checkedAt: ['checkedAt', '核对日期'],
  engineKinds: ['engineKinds', '引擎支持的检查类型'],
  },
}

/** Fields the material must carry somewhere for the reader to accept it. */
export const REQUIRE_ANY_OF = [
  '规则编号',
  'ruleId',
  '规则标题',
  'title',
  '依据文件',
  'document',
  '摘录',
  'excerpt',
]

/**
 * Parse the material and attach its canonical field names.
 * @param source - JSON or YAML text.
 * @param target - description of where the material came from.
 * @returns the normalized table, with each row's aliases resolved to field names.
 */
export function parseMaterial(source: string, target: string): TableInput {
  const table = parseTable(source, target, {
    ...SPEC,
    ...(REQUIRE_ANY_OF === undefined ? {} : { requireAnyOf: REQUIRE_ANY_OF }),
  })
  for (const row of table.rows) canonicaliseRow(row, SPEC)
  return table
}

/**
 * Run the rule pack against the material.
 * @param input - normalized table.
 * @param ruleset - validated rule pack.
 * @param options - plugin identity, clock value, rule selection and overrides.
 * @returns the report.
 */
export function runCheck(input: TableInput, ruleset: Ruleset, options: TableCheckOptions) {
  return runTableCheck(input, ruleset, options)
}

export type { TableCheckOptions, TableInput }
