# Implementation Plan: Batch Processing Support

## Phase 1: Core Batch Processing Module [checkpoint: 81032a6]

### Task 1.1: Create batch converter module structure [abfabe0]
- [x] Create `batch_converter.py` with BatchConverter class
- [x] Define BatchResult dataclass for tracking conversion results
- [x] Define BatchProgress callback protocol for progress updates

### Task 1.2: Implement file discovery [94d8894]
- [x] Add function to resolve file paths from arguments (files, directories, globs)
- [x] Filter to only .mts/.MTS files
- [x] Validate all files exist before starting batch

### Task 1.3: Implement batch conversion logic [14aba37]
- [x] Create `convert_batch()` method that iterates through files
- [x] Call existing `convert_video()` for each file
- [x] Track success/failure for each file
- [x] Invoke progress callback after each file

### Task 1.4: Add output directory support [4af5928]
- [x] Add `output_dir` parameter to batch converter
- [x] Generate output paths in specified directory
- [x] Handle filename conflicts with numeric suffix

### Task 1.5: Phase 1 Completion
- [x] Run all tests and verify >80% coverage
- [x] Manual verification of batch module
- [x] Phase checkpoint

## Phase 2: CLI Integration [checkpoint: 684311d]

### Task 2.1: Update CLI argument parsing [546fd3e]
- [x] Modify argument parser to accept multiple input paths
- [x] Add `--output-dir` option
- [x] Add `--continue-on-error` flag
- [x] Maintain single-file backward compatibility

### Task 2.2: Integrate batch converter with CLI [521aa2e]
- [x] Detect batch vs single-file mode based on arguments
- [x] Display per-file progress during batch conversion
- [x] Show batch summary at completion

### Task 2.3: CLI error handling and exit codes [4d86691]
- [x] Return exit code 0 if all successful
- [x] Return exit code 1 if any failures
- [x] Display clear error messages for failed files

### Task 2.4: Phase 2 Completion
- [x] Run all tests and verify >80% coverage
- [x] Manual verification of CLI batch mode
- [x] Phase checkpoint

## Phase 3: GUI Integration [checkpoint: 1bdaaa3]

### Task 3.1: Add file queue UI components [f02a232]
- [x] Replace single file input with file list widget
- [x] Add "Add Files" button for multi-file selection
- [x] Add "Add Folder" button for directory selection
- [x] Add "Remove" button to remove selected files from queue
- [x] Add "Clear All" button

### Task 3.2: Update progress UI for batch mode [f02a232]
- [x] Add overall batch progress bar
- [x] Show current file being processed
- [x] Display "X of Y files" counter
- [x] Add elapsed/estimated time display

### Task 3.3: Implement batch conversion in GUI [f02a232]
- [x] Integrate BatchConverter with GUI
- [x] Update progress callback to refresh UI
- [x] Handle thread-safe UI updates

### Task 3.4: Add cancel functionality [f02a232]
- [x] Add "Cancel" button during conversion
- [x] Implement graceful cancellation (finish current file)
- [x] Update UI to show cancelled state

### Task 3.5: Batch completion and error display [f02a232]
- [x] Show summary dialog on completion
- [x] List any failed files with error reasons
- [x] Allow user to retry failed files

### Task 3.6: Phase 3 Completion [1bdaaa3]
- [x] Run all tests and verify >80% coverage
- [x] Manual verification of GUI batch mode
- [x] Phase checkpoint

## Phase 4: Documentation and Polish

### Task 4.1: Update README documentation [0655bdf]
- [x] Document CLI batch usage with examples
- [x] Document GUI batch workflow
- [x] Add troubleshooting section for batch issues

### Task 4.2: Update CLAUDE.md [00817ba]
- [x] Add batch processing to architecture section
- [x] Document new module structure

### Task 4.3: Final testing and polish
- [x] End-to-end testing with real MTS files
- [x] Performance testing with large batches
- [x] UI polish and edge case handling

### Task 4.4: Phase 4 Completion
- [ ] Final test run and coverage report
- [ ] Manual verification of complete feature
- [ ] Final phase checkpoint

## Notes
- All tasks follow TDD workflow: write tests first, then implement
- Each phase ends with verification checkpoint per workflow.md
- Existing single-file functionality must remain unchanged
