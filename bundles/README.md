# GPG files for RealMe Bundles

## Get gpg passphases

    ssh turing
    pview -d lefdev ?

You can see gpg passphrase for all Bundles.

# Create gpg file for MTS Bundle

    tar -czf MTS.tgz
    gpg -c -o MTS.tgz.gpg MTS.tgz
    # input passphase for MTS

# Decrypt gpg file for MTS Bundle

    gpg -d -o MTS.tgz MTS.tgz.gpg
    # input passphase for MTS
    tar -xzf MTS.tgz

You also need to do it for ITE and PRD
