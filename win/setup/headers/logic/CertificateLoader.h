#pragma once

namespace tp::logic {
    class CertificateLoader {
    public:
        ///@brief imports certificate to the local Windows Certificate Storage
        ///@details all files signed with the corresponding certificate will be trusted by the machine
        ///@return true - successfully imported, false - error occurred and the certificate could remain unloaded
        static bool load();

        ///@brief removes certificate from local Windows Certificate Storage
        ///@details files will not be trusted anymore
        ///@return true - successfully removed, false - error occurred and the certificate could be in the storage
        static bool remove();
    };
}