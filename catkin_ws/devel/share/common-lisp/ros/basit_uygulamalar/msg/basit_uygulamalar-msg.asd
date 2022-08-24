
(cl:in-package :asdf)

(defsystem "basit_uygulamalar-msg"
  :depends-on (:roslisp-msg-protocol :roslisp-utils )
  :components ((:file "_package")
    (:file "Mesafe" :depends-on ("_package_Mesafe"))
    (:file "_package_Mesafe" :depends-on ("_package"))
  ))