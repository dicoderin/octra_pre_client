### 🚀 Getting Started
Follow these steps to set up your project and compile your smart contract.

# Step 1: Install Rust
If you don't already have Rust installed, open your terminal and run the following one-time command. It will install the entire Rust toolchain.
```bash
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

Follow the on-screen instructions. Remember to restart your terminal after the installation is complete.

# Step 2: Create a New Library Project
We'll use Cargo, Rust's powerful package manager and build system, to create a new library project.
Create a new library project named 
```bash
"smart_contract"
```
```bash
cargo new smart_contract --lib
```

Change into the project directory
```bash
cd smart_contract
```

# Step 3: Configure for WASM
Next, you need to tell the Rust compiler to produce a WASM-compatible file. Open the Cargo.toml file and add the [lib] section as shown below.

```toml
[package]
name = "smart_contract"
version = "0.1.0"
edition = "2021"

[dependencies]

# ADD THIS SECTION
[lib]
crate-type = ["cdylib"]
```

# Step 4: Write a Simple Contract
Open the src/lib.rs file and replace its contents with the simple contract code below. This contract contains a single function that adds two numbers.

```bash
// Prevents the compiler from changing the function's name
#[no_mangle]
// Exposes this function to be called from outside the WASM module
pub extern "C" fn add(a: i32, b: i32) -> i32 {
    // Simple smart contract logic
    a + b
}
```

# Step 5: Compile to WASM
Now it's time to compile your Rust code into a .wasm file.

* Add the wasm32 compile target if you haven't already
```bash
rustup target add wasm32-unknown-unknown
```

* Compile the project to the WASM target in release mode
```bash
cargo build --target wasm32-unknown-unknown --release
```


If the build is successful, you will find your compiled bytecode at:
```bash
target/wasm32-unknown-unknown/release/smart_contract.wasm
```
That's your .wasm file! 🎉


* 🏁 Next Steps
With the smart_contract.wasm file from Step 5, you can now use the Python client you've built to deploy it to the blockchain via the [D] Deploy Contract menu.
This separation of the compilation process (using cargo) and the deployment process (using a Python client) represents a clean, standard, and professional workflow.
