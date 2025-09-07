# Code Quality Audit Report

## Project Metrics

- **Total Files:** 148
- **Python Files:** 25
- **Shell Scripts:** 32
- **Config Files:** 19
- **Lines of Code:** 4714
- **Functions:** 108
- **Classes:** 15

**Total Quality Issues:** 225

- **MEDIUM:** 84 issues
- **LOW:** 134 issues
- **INFO:** 7 issues

## Detailed Findings

### MEDIUM Severity

**1. Project Structure**
- Description: Missing essential file: LICENSE

**2. Code Complexity**
- Description: High cyclomatic complexity in function verify_security_fixes: 15
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/verify_audit_completion.py`
- Line: 11

**3. Code Complexity**
- Description: High cyclomatic complexity in function _check_python_code_smells: 11
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 169

**4. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 186

**5. Code Style**
- Description: Wildcard import detected
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`

**6. Code Complexity**
- Description: High cyclomatic complexity in function fix_hardcoded_credentials: 11
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 22

**7. Code Complexity**
- Description: High cyclomatic complexity in function chat_with_ollama: 12
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/chat_demo.py`
- Line: 9

**8. Code Complexity**
- Description: High cyclomatic complexity in function check_service_connections: 17
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/verify_connections.py`
- Line: 16

**9. Code Complexity**
- Description: High cyclomatic complexity in function route_task: 11
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 137

**10. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 214

**11. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 215

**12. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 216

**13. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 217

**14. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 218

**15. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 219

**16. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 220

**17. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 221

**18. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 222

**19. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 223

**20. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 224

**21. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 225

**22. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 226

**23. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 230

**24. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 231

**25. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 232

**26. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 236

**27. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 237

**28. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 240

**29. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 242

**30. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 243

**31. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 244

**32. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 246

**33. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 249

**34. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 251

**35. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 252

**36. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 253

**37. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 255

**38. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 257

**39. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 261

**40. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 262

**41. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 268

**42. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 270

**43. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 271

**44. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 275

**45. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 276

**46. Code Complexity**
- Description: High cyclomatic complexity in function main: 12
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/run.py`
- Line: 14

**47. Code Complexity**
- Description: High cyclomatic complexity in function auto_login: 19
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 15

**48. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_openhands.sh`

**49. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/stop_services.sh`

**50. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/optimize.sh`

**51. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/essential_commands.sh`

**52. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_ollama.sh`

**53. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_vllm.sh`

**54. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/backup.sh`

**55. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_llmstack.sh`

**56. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/validate.sh`

**57. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/start_services.sh`

**58. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_jan.sh`

**59. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_lm_studio.sh`

**60. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_pipeline.sh`

**61. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_aider.sh`

**62. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_flowise.sh`

**63. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_continue.sh`

**64. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_agents.sh`

**65. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/validate_deployment.sh`

**66. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/optimize_system.sh`

**67. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/benchmark.sh`

**68. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_ollama.sh`

**69. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/setup_vllm.sh`

**70. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/manage_services.sh`

**71. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/check_system.sh`

**72. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_jan.sh`

**73. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_lm_studio.sh`

**74. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/setup_monitoring.sh`

**75. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/troubleshoot.sh`

**76. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_continue.sh`

**77. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/deploy_llmstack.sh`

**78. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/apps/code_pipeline.sh`

**79. Dependencies**
- Description: Unpinned dependency: autogen-agentchat
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 14

**80. Dependencies**
- Description: Unpinned dependency: aider-chat
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 17

**81. Dependencies**
- Description: Unpinned dependency: jq
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 34

**82. Dependencies**
- Description: Unpinned dependency: jupyter
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 37

**83. Dependencies**
- Description: Unpinned dependency: ipywidgets
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 38

**84. Testing**
- Description: No test files found

### LOW Severity

**1. Project Structure**
- Description: Missing recommended directory: docs

**2. Project Structure**
- Description: Missing recommended directory: tests

**3. Code Style**
- Description: Long function verify_security_fixes: 60 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/verify_audit_completion.py`
- Line: 11

**4. Code Style**
- Description: Line too long (92 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/verify_audit_completion.py`
- Line: 25

**5. Code Style**
- Description: Line too long (96 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/verify_audit_completion.py`
- Line: 26

**6. Code Style**
- Description: Line too long (89 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/verify_audit_completion.py`
- Line: 28

**7. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/verify_audit_completion.py`
- Line: 63

**8. Code Style**
- Description: Line too long (90 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/verify_audit_completion.py`
- Line: 134

**9. Code Style**
- Description: Line too long (102 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/verify_audit_completion.py`
- Line: 135

**10. Code Style**
- Description: Line too long (119 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 28

**11. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 42

**12. Code Style**
- Description: Line too long (89 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 43

**13. Code Style**
- Description: Line too long (103 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 44

**14. Code Style**
- Description: Line too long (92 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 45

**15. Code Style**
- Description: Line too long (109 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 53

**16. Code Style**
- Description: Line too long (111 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 68

**17. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 72

**18. Code Style**
- Description: Line too long (98 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 78

**19. Code Style**
- Description: Line too long (107 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 82

**20. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 87

**21. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 104

**22. Code Style**
- Description: Line too long (120 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 115

**23. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 148

**24. Code Style**
- Description: Line too long (142 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 152

**25. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 183

**26. Code Style**
- Description: Line too long (106 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 208

**27. Code Style**
- Description: Line too long (104 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 218

**28. Code Style**
- Description: Line too long (89 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 228

**29. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 240

**30. Code Style**
- Description: Line too long (142 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 252

**31. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 265

**32. Code Style**
- Description: Long function _check_python_code_smells: 52 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 169

**33. Code Style**
- Description: Line too long (119 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 35

**34. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 59

**35. Code Style**
- Description: Line too long (104 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 112

**36. Code Style**
- Description: Line too long (92 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 127

**37. Code Style**
- Description: Line too long (96 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 133

**38. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 261

**39. Code Style**
- Description: Line too long (105 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 266

**40. Code Style**
- Description: Line too long (99 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 297

**41. Code Style**
- Description: Line too long (106 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 298

**42. Code Style**
- Description: Line too long (104 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 307

**43. Code Style**
- Description: Line too long (96 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 313

**44. Code Style**
- Description: Line too long (105 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 358

**45. Code Style**
- Description: Line too long (104 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 396

**46. Code Style**
- Description: Line too long (118 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 420

**47. Code Style**
- Description: Long function generate_executive_summary: 77 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 28

**48. Code Style**
- Description: Long function generate_technical_details: 104 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 107

**49. Code Style**
- Description: Long function generate_action_plan: 166 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 213

**50. Code Style**
- Description: Long function generate_full_report: 58 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 381

**51. Code Style**
- Description: Line too long (214 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 34

**52. Code Style**
- Description: Line too long (90 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 39

**53. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 40

**54. Code Style**
- Description: Line too long (96 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 41

**55. Code Style**
- Description: Line too long (90 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 42

**56. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 43

**57. Code Style**
- Description: Line too long (289 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 418

**58. Code Style**
- Description: Line too long (253 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 420

**59. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 423

**60. Code Style**
- Description: Line too long (103 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 424

**61. Code Style**
- Description: Line too long (92 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 425

**62. Code Style**
- Description: Line too long (147 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/audit_report_generator.py`
- Line: 436

**63. Code Style**
- Description: Long function fix_hardcoded_credentials: 70 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 22

**64. Code Style**
- Description: Long function create_env_template: 57 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 94

**65. Code Style**
- Description: Long function update_gitignore: 56 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 153

**66. Code Style**
- Description: Long function create_security_checklist: 72 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 236

**67. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/benchmark_system.py`
- Line: 87

**68. Code Style**
- Description: Line too long (112 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/benchmark_system.py`
- Line: 137

**69. Code Style**
- Description: Long function configure_providers: 61 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/configure_providers.py`
- Line: 28

**70. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/configure_providers.py`
- Line: 70

**71. Code Style**
- Description: Line too long (90 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/configure_providers.py`
- Line: 84

**72. Code Style**
- Description: Long function test_flowise: 51 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/test_flowise.py`
- Line: 15

**73. Code Style**
- Description: Long function chat_with_ollama: 76 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/chat_demo.py`
- Line: 9

**74. Code Style**
- Description: Line too long (92 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/chat_demo.py`
- Line: 69

**75. Code Style**
- Description: Line too long (98 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/TEST_OLLAMA.py`
- Line: 83

**76. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/ai_frameworks_integration.py`
- Line: 119

**77. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/ai_frameworks_integration.py`
- Line: 208

**78. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/ai_frameworks_integration.py`
- Line: 401

**79. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/extract_docx.py`
- Line: 15

**80. Code Style**
- Description: Line too long (90 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/extract_docx.py`
- Line: 41

**81. Code Style**
- Description: Long function main: 71 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/health_check.py`
- Line: 97

**82. Code Style**
- Description: Long function check_service_connections: 183 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/verify_connections.py`
- Line: 16

**83. Code Style**
- Description: Line too long (114 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/verify_connections.py`
- Line: 142

**84. Code Style**
- Description: Line too long (108 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/verify_connections.py`
- Line: 143

**85. Code Style**
- Description: Long function index: 101 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 206

**86. Code Style**
- Description: Line too long (96 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 134

**87. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 190

**88. Code Style**
- Description: Line too long (116 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 215

**89. Code Style**
- Description: Line too long (126 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 217

**90. Code Style**
- Description: Line too long (98 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 221

**91. Code Style**
- Description: Line too long (125 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 222

**92. Code Style**
- Description: Line too long (128 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 223

**93. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 225

**94. Code Style**
- Description: Line too long (99 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 244

**95. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 253

**96. Code Style**
- Description: Line too long (115 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 271

**97. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 289

**98. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/run.py`
- Line: 42

**99. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/run.py`
- Line: 44

**100. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/run.py`
- Line: 56

**101. Code Style**
- Description: Long function auto_login: 70 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 15

**102. Code Style**
- Description: Line too long (97 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 56

**103. Code Style**
- Description: Long function dev_team_example: 74 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 54

**104. Code Style**
- Description: Long function research_team_example: 56 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 131

**105. Code Style**
- Description: Long function code_review_example: 61 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 190

**106. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 33

**107. Code Style**
- Description: Line too long (135 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 186

**108. Code Style**
- Description: Line too long (108 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 214

**109. Code Style**
- Description: Line too long (114 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 221

**110. Code Style**
- Description: Line too long (111 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 228

**111. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 261

**112. Code Style**
- Description: Line too long (113 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 268

**113. Code Style**
- Description: Line too long (105 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 275

**114. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/src/tests/test_main.py`
- Line: 91

**115. Shell Scripts**
- Description: Potentially unquoted variables: $LLMSTACK_HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/backup.sh`

**116. Shell Scripts**
- Description: Potentially unquoted variables: $HOME, $LLMSTACK_HOM, $LLMSTACK_HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_llmstack.sh`

**117. Shell Scripts**
- Description: Potentially unquoted variables: $respons, $ur, $name
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/validate.sh`

**118. Shell Scripts**
- Description: Potentially unquoted variables: $LLMSTACK_HOM
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/start_services.sh`

**119. Shell Scripts**
- Description: Potentially unquoted variables: $HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_lm_studio.sh`

**120. Shell Scripts**
- Description: Potentially unquoted variables: $REQUIREMENTS, $PROJECT_NAM, $PROJECT_NAME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_pipeline.sh`

**121. Shell Scripts**
- Description: Potentially unquoted variables: $respons, $ur, $name
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/validate_deployment.sh`

**122. Shell Scripts**
- Description: Potentially unquoted variables: $end_time, $model, $respons, $endpoint, $name
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/benchmark.sh`

**123. Shell Scripts**
- Description: Potentially unquoted variables: $COMMAN
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/manage_services.sh`

**124. Shell Scripts**
- Description: Potentially unquoted variables: $CPU_CORES, $RAM_GB, $RAM_G, $CPU_CORE, $VRAM_M
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/check_system.sh`

**125. Shell Scripts**
- Description: Potentially unquoted variables: $HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_lm_studio.sh`

**126. Shell Scripts**
- Description: Potentially unquoted variables: $port, $service
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/troubleshoot.sh`

**127. Shell Scripts**
- Description: Potentially unquoted variables: $HOME, $LLMSTACK_HOM, $LLMSTACK_HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/deploy_llmstack.sh`

**128. Shell Scripts**
- Description: Potentially unquoted variables: $REQUIREMENT, $PROJECT_NAM
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/apps/code_pipeline.sh`

**129. Documentation**
- Description: Documentation contains localhost link: http://localhost:3000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/README_CLEAN.md`

**130. Documentation**
- Description: Documentation contains localhost link: http://localhost:3001
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/README_CLEAN.md`

**131. Documentation**
- Description: Documentation contains localhost link: http://localhost:8080/swagger
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/README_CLEAN.md`

**132. Documentation**
- Description: Very short documentation file
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/.github/copilot-instructions.md`

**133. Dependencies**
- Description: Potentially risky dependency: pyyaml>=6.0
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 25

**134. Dependencies**
- Description: Potentially risky dependency: pyyaml>=6.0.1
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/requirements.txt`
- Line: 52

### INFO Severity

**1. Documentation**
- Description: TODO/FIXME comment found
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 195

**2. Documentation**
- Description: TODO/FIXME comment found
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 196

**3. Documentation**
- Description: TODO/FIXME comment found
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 200

**4. Documentation**
- Description: TODO/FIXME comment found
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 123

**5. Documentation**
- Description: TODO/FIXME comment found
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 125

**6. Configuration**
- Description: Configuration contains placeholder credentials
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.development.yml`

**7. Configuration**
- Description: Configuration contains placeholder credentials
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/flowise_agent_flow.json`

