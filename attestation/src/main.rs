use std::{env, error::Error};

use aws_nitro_enclaves_nsm_api::{
    api::{Request, Response},
    driver::{nsm_exit, nsm_init, nsm_process_request},
};
use serde_bytes::ByteBuf;

/// Forward a request to the NSM and return its response.
///
/// Provide user data, nonce and public key, in this order, as arguments. Provide an empty string
/// for missing arguments.
fn main() -> Result<(), Box<dyn Error>> {
    let args: Result<[_; 3], _> = env::args()
        // Skip binary name
        .skip(1)
        .map(|arg| Some(ByteBuf::from(arg)))
        .collect::<Vec<_>>()
        .try_into();

    let nsm_fd = nsm_init();

    let result: Result<(), Box<dyn Error>> = 'nsm: {
        let (user_data, nonce, public_key) = if let Ok(args) = args {
            args.into()
        } else {
            break 'nsm Err(
                "Attestation should be called with `user_data`, `nonce` and `public_key`".into(),
            );
        };

        let request = Request::Attestation {
            user_data,
            nonce,
            public_key,
        };

        match nsm_process_request(nsm_fd, request) {
            Response::Attestation { document } => {
                let document = hex::encode(document);
                println!("Success: {document}");
                Ok(())
            }
            Response::Error(code) => Err(format!("{code:?}").into()),
            response => Err(format!("Unexpected response: {response:?}").into()),
        }
    };

    nsm_exit(nsm_fd);

    result
}
