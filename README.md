memdetect
=========

Utility scripts used in my research [Uninitialized Memory Dislosures in Web Applications](https://www.sans.org/reading-room/whitepapers/webappsec/uninitialized-memory-disclosures-web-applications-39460).

* collect.py - Simple _requests_ based script for bulk image upload and collection.
* detect.py - Test and compare memory leak detection algorithms for images.
* fill_idat.py - Fill PNG's with a single color to generate test cases. 
* oracle.py - Evaluate results of `detect.py` based on file name oracle. 

Use the `--help` option of each script for more information. 

