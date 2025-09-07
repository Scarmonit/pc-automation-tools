# Code Quality Audit Report

## Project Metrics

- **Total Files:** 143
- **Python Files:** 23
- **Shell Scripts:** 32
- **Config Files:** 18
- **Lines of Code:** 4104
- **Functions:** 98
- **Classes:** 15

**Total Quality Issues:** 200

- **MEDIUM:** 83 issues
- **LOW:** 110 issues
- **INFO:** 7 issues

## Detailed Findings

### MEDIUM Severity

**1. Project Structure**
- Description: Missing essential file: LICENSE

**2. Code Complexity**
- Description: High cyclomatic complexity in function _check_python_code_smells: 11
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 169

**3. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 186

**4. Code Style**
- Description: Wildcard import detected
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`

**5. Code Complexity**
- Description: High cyclomatic complexity in function fix_hardcoded_credentials: 11
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 22

**6. Code Complexity**
- Description: High cyclomatic complexity in function chat_with_ollama: 12
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/chat_demo.py`
- Line: 9

**7. Code Complexity**
- Description: High cyclomatic complexity in function check_service_connections: 17
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/verify_connections.py`
- Line: 16

**8. Code Complexity**
- Description: High cyclomatic complexity in function route_task: 11
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 137

**9. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 214

**10. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 215

**11. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 216

**12. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 217

**13. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 218

**14. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 219

**15. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 220

**16. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 221

**17. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 222

**18. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 223

**19. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 224

**20. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 225

**21. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 226

**22. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 230

**23. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 231

**24. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 232

**25. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 236

**26. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 237

**27. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 240

**28. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 242

**29. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 243

**30. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 244

**31. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 246

**32. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 249

**33. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 251

**34. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 252

**35. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 253

**36. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 255

**37. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 257

**38. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 261

**39. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 262

**40. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 268

**41. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 270

**42. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 271

**43. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 275

**44. Code Style**
- Description: Multiple statements on one line
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 276

**45. Code Complexity**
- Description: High cyclomatic complexity in function main: 12
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/run.py`
- Line: 14

**46. Code Complexity**
- Description: High cyclomatic complexity in function auto_login: 19
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 15

**47. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_openhands.sh`

**48. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/stop_services.sh`

**49. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/optimize.sh`

**50. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/essential_commands.sh`

**51. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_ollama.sh`

**52. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_vllm.sh`

**53. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/backup.sh`

**54. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_llmstack.sh`

**55. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/validate.sh`

**56. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/start_services.sh`

**57. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_jan.sh`

**58. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_lm_studio.sh`

**59. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_pipeline.sh`

**60. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_aider.sh`

**61. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_flowise.sh`

**62. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_continue.sh`

**63. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_agents.sh`

**64. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/validate_deployment.sh`

**65. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/optimize_system.sh`

**66. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/benchmark.sh`

**67. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_ollama.sh`

**68. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/setup_vllm.sh`

**69. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/manage_services.sh`

**70. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/check_system.sh`

**71. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_jan.sh`

**72. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_lm_studio.sh`

**73. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/setup_monitoring.sh`

**74. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/troubleshoot.sh`

**75. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_continue.sh`

**76. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/deploy_llmstack.sh`

**77. Shell Scripts**
- Description: Missing "set -e" for error handling
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/apps/code_pipeline.sh`

**78. Dependencies**
- Description: Unpinned dependency: autogen-agentchat
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 14

**79. Dependencies**
- Description: Unpinned dependency: aider-chat
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 17

**80. Dependencies**
- Description: Unpinned dependency: jq
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 34

**81. Dependencies**
- Description: Unpinned dependency: jupyter
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 37

**82. Dependencies**
- Description: Unpinned dependency: ipywidgets
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 38

**83. Testing**
- Description: No test files found

### LOW Severity

**1. Project Structure**
- Description: Missing recommended directory: docs

**2. Project Structure**
- Description: Missing recommended directory: tests

**3. Code Style**
- Description: Line too long (119 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 28

**4. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 42

**5. Code Style**
- Description: Line too long (89 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 43

**6. Code Style**
- Description: Line too long (103 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 44

**7. Code Style**
- Description: Line too long (92 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 45

**8. Code Style**
- Description: Line too long (109 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 53

**9. Code Style**
- Description: Line too long (111 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 68

**10. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 72

**11. Code Style**
- Description: Line too long (98 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 78

**12. Code Style**
- Description: Line too long (107 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 82

**13. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 87

**14. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 104

**15. Code Style**
- Description: Line too long (120 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 115

**16. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 148

**17. Code Style**
- Description: Line too long (142 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 152

**18. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 183

**19. Code Style**
- Description: Line too long (106 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 208

**20. Code Style**
- Description: Line too long (104 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 218

**21. Code Style**
- Description: Line too long (89 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 228

**22. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 240

**23. Code Style**
- Description: Line too long (142 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 252

**24. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_audit.py`
- Line: 265

**25. Code Style**
- Description: Long function _check_python_code_smells: 52 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 169

**26. Code Style**
- Description: Line too long (119 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 35

**27. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 59

**28. Code Style**
- Description: Line too long (104 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 112

**29. Code Style**
- Description: Line too long (92 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 127

**30. Code Style**
- Description: Line too long (96 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 133

**31. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 261

**32. Code Style**
- Description: Line too long (105 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 266

**33. Code Style**
- Description: Line too long (99 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 297

**34. Code Style**
- Description: Line too long (106 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 298

**35. Code Style**
- Description: Line too long (104 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 307

**36. Code Style**
- Description: Line too long (96 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 313

**37. Code Style**
- Description: Line too long (105 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 358

**38. Code Style**
- Description: Line too long (104 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 396

**39. Code Style**
- Description: Line too long (118 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_quality_audit.py`
- Line: 420

**40. Code Style**
- Description: Long function fix_hardcoded_credentials: 70 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 22

**41. Code Style**
- Description: Long function create_env_template: 57 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 94

**42. Code Style**
- Description: Long function update_gitignore: 56 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 153

**43. Code Style**
- Description: Long function create_security_checklist: 72 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/security_fix.py`
- Line: 236

**44. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/benchmark_system.py`
- Line: 87

**45. Code Style**
- Description: Line too long (112 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/benchmark_system.py`
- Line: 137

**46. Code Style**
- Description: Long function configure_providers: 61 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/configure_providers.py`
- Line: 28

**47. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/configure_providers.py`
- Line: 70

**48. Code Style**
- Description: Line too long (90 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/configure_providers.py`
- Line: 84

**49. Code Style**
- Description: Long function test_flowise: 51 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/test_flowise.py`
- Line: 15

**50. Code Style**
- Description: Long function chat_with_ollama: 76 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/chat_demo.py`
- Line: 9

**51. Code Style**
- Description: Line too long (92 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/chat_demo.py`
- Line: 69

**52. Code Style**
- Description: Line too long (98 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/TEST_OLLAMA.py`
- Line: 83

**53. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/ai_frameworks_integration.py`
- Line: 119

**54. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/ai_frameworks_integration.py`
- Line: 208

**55. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/ai_frameworks_integration.py`
- Line: 401

**56. Code Style**
- Description: Line too long (93 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/extract_docx.py`
- Line: 15

**57. Code Style**
- Description: Line too long (90 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/extract_docx.py`
- Line: 41

**58. Code Style**
- Description: Long function main: 71 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/health_check.py`
- Line: 97

**59. Code Style**
- Description: Long function check_service_connections: 183 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/verify_connections.py`
- Line: 16

**60. Code Style**
- Description: Line too long (114 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/verify_connections.py`
- Line: 142

**61. Code Style**
- Description: Line too long (108 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/verify_connections.py`
- Line: 143

**62. Code Style**
- Description: Long function index: 101 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 206

**63. Code Style**
- Description: Line too long (96 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 134

**64. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 190

**65. Code Style**
- Description: Line too long (116 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 215

**66. Code Style**
- Description: Line too long (126 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 217

**67. Code Style**
- Description: Line too long (98 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 221

**68. Code Style**
- Description: Line too long (125 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 222

**69. Code Style**
- Description: Line too long (128 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 223

**70. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 225

**71. Code Style**
- Description: Line too long (99 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 244

**72. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 253

**73. Code Style**
- Description: Line too long (115 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 271

**74. Code Style**
- Description: Line too long (101 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/unified_orchestrator.py`
- Line: 289

**75. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/run.py`
- Line: 42

**76. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/run.py`
- Line: 44

**77. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/run.py`
- Line: 56

**78. Code Style**
- Description: Long function auto_login: 70 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 15

**79. Code Style**
- Description: Line too long (97 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/auto_login.py`
- Line: 56

**80. Code Style**
- Description: Long function dev_team_example: 74 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 54

**81. Code Style**
- Description: Long function research_team_example: 56 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 131

**82. Code Style**
- Description: Long function code_review_example: 61 lines
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 190

**83. Code Style**
- Description: Line too long (91 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 33

**84. Code Style**
- Description: Line too long (135 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 186

**85. Code Style**
- Description: Line too long (108 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 214

**86. Code Style**
- Description: Line too long (114 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 221

**87. Code Style**
- Description: Line too long (111 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 228

**88. Code Style**
- Description: Line too long (95 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 261

**89. Code Style**
- Description: Line too long (113 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 268

**90. Code Style**
- Description: Line too long (105 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/examples/04_autogen_agents.py`
- Line: 275

**91. Code Style**
- Description: Line too long (94 characters)
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/src/tests/test_main.py`
- Line: 91

**92. Shell Scripts**
- Description: Potentially unquoted variables: $LLMSTACK_HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/backup.sh`

**93. Shell Scripts**
- Description: Potentially unquoted variables: $LLMSTACK_HOM, $HOME, $LLMSTACK_HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/setup_llmstack.sh`

**94. Shell Scripts**
- Description: Potentially unquoted variables: $respons, $ur, $name
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/validate.sh`

**95. Shell Scripts**
- Description: Potentially unquoted variables: $LLMSTACK_HOM
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/start_services.sh`

**96. Shell Scripts**
- Description: Potentially unquoted variables: $HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/install_lm_studio.sh`

**97. Shell Scripts**
- Description: Potentially unquoted variables: $PROJECT_NAME, $PROJECT_NAM, $REQUIREMENTS
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/code_pipeline.sh`

**98. Shell Scripts**
- Description: Potentially unquoted variables: $respons, $ur, $name
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/validate_deployment.sh`

**99. Shell Scripts**
- Description: Potentially unquoted variables: $name, $model, $endpoint, $respons, $end_time
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/benchmark.sh`

**100. Shell Scripts**
- Description: Potentially unquoted variables: $COMMAN
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/manage_services.sh`

**101. Shell Scripts**
- Description: Potentially unquoted variables: $VRAM_M, $RAM_GB, $CPU_CORE, $CPU_CORES, $RAM_G
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/check_system.sh`

**102. Shell Scripts**
- Description: Potentially unquoted variables: $HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/install_lm_studio.sh`

**103. Shell Scripts**
- Description: Potentially unquoted variables: $service, $port
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/troubleshoot.sh`

**104. Shell Scripts**
- Description: Potentially unquoted variables: $LLMSTACK_HOM, $HOME, $LLMSTACK_HOME
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/scripts/deploy_llmstack.sh`

**105. Shell Scripts**
- Description: Potentially unquoted variables: $REQUIREMENT, $PROJECT_NAM
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/apps/code_pipeline.sh`

**106. Documentation**
- Description: Documentation contains localhost link: http://localhost:3000
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/README_CLEAN.md`

**107. Documentation**
- Description: Documentation contains localhost link: http://localhost:3001
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/README_CLEAN.md`

**108. Documentation**
- Description: Documentation contains localhost link: http://localhost:8080/swagger
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/README_CLEAN.md`

**109. Dependencies**
- Description: Potentially risky dependency: pyyaml>=6.0
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/requirements.txt`
- Line: 25

**110. Dependencies**
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
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/llmstack/flowise_agent_flow.json`

**7. Configuration**
- Description: Configuration contains placeholder credentials
- File: `/home/runner/work/pc-automation-tools/pc-automation-tools/docker-compose.development.yml`

