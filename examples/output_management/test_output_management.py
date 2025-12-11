"""Quick test script to verify output management implementation."""

# This script can be run to quickly test the output management system
# without needing to set up a full pipeline

import sys
from pathlib import Path

# Add parent directory to path to import lw_pipeline
sys.path.insert(0, str(Path(__file__).parent.parent))

from lw_pipeline import Config, Pipeline_Step, register_output

# Create a minimal config
class TestConfig:
    """Minimal config for testing."""
    overwrite_mode = "always"
    output_profiling = True
    sidecar_auto_generate = True
    output_root = Path(__file__).parent / "test_outputs"
    deriv_root = output_root
    outputs_to_generate = None
    
    def get_version(self):
        return "test-version"
    
    def ask(self, message, default="n"):
        return default


class TestStep(Pipeline_Step):
    """Test step with registered outputs."""
    
    @register_output("test_output", "Test output", enabled_by_default=True)
    def create_output(self):
        """Create a test output."""
        if not self.should_generate_output("test_output"):
            print("  ⊗ Skipping test_output")
            return
        
        print("  ✓ Generating test_output")
        
        # Test text saving
        self.output_manager.save_text(
            "This is a test output",
            name="test_file",
            suffix="log",
            metadata={"test": True},
            use_bids_structure=False
        )
    
    @register_output("disabled_output", "Disabled output", enabled_by_default=False)
    def create_disabled_output(self):
        """Create a disabled output."""
        if not self.should_generate_output("disabled_output"):
            print("  ⊗ Skipping disabled_output (disabled by default)")
            return
        
        print("  ✓ Generating disabled_output")
        
        self.output_manager.save_text(
            "This output is disabled by default",
            name="disabled_file",
            use_bids_structure=False
        )
    
    def step(self, data):
        """Execute the test step."""
        print("\nExecuting test step...")
        self.create_output()
        self.create_disabled_output()
        return data


def test_basic_functionality():
    """Test basic output management functionality."""
    print("="*80)
    print("Testing Output Management System")
    print("="*80)
    
    # Create config and step
    config = TestConfig()
    step = TestStep("Test step", config, short_id="00")
    
    # Test 1: Default behavior
    print("\nTest 1: Default behavior (only enabled outputs)")
    print("-"*80)
    step.step(None)
    
    # Test 2: Generate all outputs
    print("\nTest 2: Generate all outputs (including disabled)")
    print("-"*80)
    config.outputs_to_generate = ["*"]
    step.step(None)
    
    # Test 3: Generate specific output
    print("\nTest 3: Generate only disabled_output")
    print("-"*80)
    config.outputs_to_generate = ["disabled_output"]
    step.step(None)
    
    # Test 4: Check output registry
    print("\nTest 4: List registered outputs")
    print("-"*80)
    outputs = step.output_registry.list_outputs()
    for name, desc, enabled in outputs:
        status = "enabled" if enabled else "disabled"
        print(f"  - {name}: {desc} ({status})")
    
    # Test 5: Check generated files
    print("\nTest 5: Check generated files")
    print("-"*80)
    output_dir = config.output_root
    if output_dir.exists():
        files = sorted(output_dir.iterdir())
        print(f"  Found {len(files)} files in {output_dir}:")
        for f in files:
            print(f"    - {f.name}")
    else:
        print(f"  Output directory not found: {output_dir}")
    
    print("\n" + "="*80)
    print("Tests completed!")
    print("="*80)
    
    # Cleanup
    print("\nNote: Test outputs saved to:", config.output_root)
    print("You can delete this directory if no longer needed.")


if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
