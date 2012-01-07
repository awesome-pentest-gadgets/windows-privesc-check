from wpc.file import file as File
from wpc.groups import groups
from wpc.parseOptions import parseOptions
from wpc.processes import processes
from wpc.regkey import regkey
from wpc.report.fileAcl import fileAcl
from wpc.report.report import report
from wpc.services import drivers, services
from wpc.users import users
from wpc.shares import shares
from wpc.utils import k32, wow64
import ctypes
import os
import wpc.conf
import wpc.utils
import glob


# ---------------------- Define Subs ---------------------------
def dump_paths(report):
    # TODO
    print "[E] dump_paths not implemented yet.  Sorry."


def dump_eventlogs(report):
    # TODO
    print "[E] dump_eventlogs not implemented yet.  Sorry."


def dump_shares(report):
    for s in shares().get_all():
        print s.as_text()


def dump_patches(report):
    # TODO
    print "[E] dump_patches not implemented yet.  Sorry."


def dump_loggedin(report):
    # TODO
    print "[E] dump_loggedin not implemented yet.  Sorry."


def dump_program_files(report):
    # TODO
    print "[E] dump_program_files not implemented yet.  Sorry."


def dump_services(opts):
    for s in services().get_services():
        if opts.ignore_trusted:
            print s.untrusted_as_text()
        else:
            print s.as_text()


def dump_drivers(opts):
    for d in drivers().get_services():
        if opts.ignore_trusted:
            print d.untrusted_as_text()
        else:
            print d.as_text()


def dump_processes(opts):
    for p in processes().get_all():
        print p.as_text()

        # When listing DLLs for a process we need to see the filesystem like they do
        if p.is_wow64():
            k32.Wow64EnableWow64FsRedirection(ctypes.byref(wow64))

        if p.get_exe():
            print "Security Descriptor for Exe File %s" % p.get_exe().get_name()
            if p.get_exe().get_sd():
                print p.get_exe().get_sd().as_text()
            else:
                print "[unknown]"

            for dll in p.get_dlls():
                print "\nSecurity Descriptor for DLL File %s" % dll.get_name()
                print dll.get_sd().as_text()

        if p.is_wow64():
            k32.Wow64DisableWow64FsRedirection(ctypes.byref(wow64))


def dump_users(opts):
    print "[+] Dumping user list:"
    userlist = users()
    for u in userlist.get_all():
        print u.get_fq_name()

#        if opts.get_privs:
        print "\n\t[+] Privileges of this user:"
        for priv in u.get_privileges():
            print "\t%s" % priv

        print "\n\t[+] Privileges of this user + the groups it is in:"
        for p in u.get_effective_privileges():
            print "\t%s" % p
        print


def dump_groups(opts):
    print "[+] Dumping group list:"
    grouplist = groups()
    for g in grouplist.get_all():
        print g.get_fq_name()

        #if opts.get_members:
        print "\n\t[+] Members:"
        for m in g.get_members():
            print "\t%s" % m.get_fq_name()

        #if opts.get_privs:
        print "\n\t[+] Privileges of this group:"
        for priv in g.get_privileges():
            print "\t%s" % priv

        # TODO
        # print "\n\t[+] Privileges of this group + the groups it is in:"
        # for p in g.get_effective_privileges():
        #    print "\t%s" % p


def dump_registry(opts):
    # TODO
    print "[!] Registry dump option not implemented yet.  Sorry."


def audit_eventlogs(report):
    # TODO
    print "[E] audit_eventlogs not implemented yet.  Sorry."


def audit_shares(report):
    # TODO
    print "[E] audit_shares not implemented yet.  Sorry."


def audit_patches(report):
    # TODO
    print "[E] audit_patches not implemented yet.  Sorry."


def audit_loggedin(report):
    # TODO
    print "[E] audit_loggedin not implemented yet.  Sorry."


def audit_drivers(report):
    # TODO
    print "[!] Driver audit option not implemented yet.  Sorry."


def audit_processes(report):
    for p in processes().get_all():
        #print p.as_text()

        #print "[D] Dangerous process perms"
        # TODO check the dangerous perms aren't held by the process owner
        if p.get_sd():
            perms = p.get_sd().get_acelist().get_untrusted().get_dangerous_perms().get_aces()
            for perm in perms:
                    report.get_by_id("WPC069").add_supporting_data('process_perms', [p, perm])
        #print "[D] End"

        # When listing DLLs for a process we need to see the filesystem like they do
        if p.is_wow64():
            k32.Wow64EnableWow64FsRedirection(ctypes.byref(wow64))

        if p.get_exe():
            if p.get_exe().is_replaceable():
                report.get_by_id("WPC067").add_supporting_data('process_exe', [p])
                #print "[D] Security Descriptor for replaceable Exe File %s" % p.get_exe().get_name()
                #if p.get_exe().get_sd():
                #    print p.get_exe().get_sd().as_text()
                #else:
                #    print "[unknown]"

                for dll in p.get_dlls():
                    if dll.is_replaceable():
                        report.get_by_id("WPC068").add_supporting_data('process_dll', [p, dll])
                        #print "\nSecurity Descriptor for replaceable DLL File %s" % dll.get_name()
                        #print dll.get_sd().as_text()

        if p.is_wow64():
            k32.Wow64DisableWow64FsRedirection(ctypes.byref(wow64))


def audit_users(report):
    userlist = users()
    for u in userlist.get_all():
        # print u.get_fq_name()

        # TODO consider other privs too
        # TODO remove useless privs
        # TODO More efficient method that doesn't involve looping through all users?  What does secpol.msc do?
        for p in u.get_effective_privileges():
            # print "\t%s" % p
            if p == "SeAssignPrimaryTokenPrivilege":
                report.get_by_id("WPC070").add_supporting_data('user_powerful_priv', [u])
            if p == "SeBackupPrivilege":
                report.get_by_id("WPC071").add_supporting_data('user_powerful_priv', [u])
            if p == "SeCreatePagefilePrivilege":
                report.get_by_id("WPC072").add_supporting_data('user_powerful_priv', [u])
            if p == "SeCreateTokenPrivilege":
                report.get_by_id("WPC073").add_supporting_data('user_powerful_priv', [u])
            if p == "SeDebugPrivilege":
                report.get_by_id("WPC074").add_supporting_data('user_powerful_priv', [u])
            if p == "SeEnableDelegationPrivilege":
                report.get_by_id("WPC075").add_supporting_data('user_powerful_priv', [u])
            if p == "SeLoadDriverPrivilege":
                report.get_by_id("WPC076").add_supporting_data('user_powerful_priv', [u])
            if p == "SeMachineAccountPrivilege":
                report.get_by_id("WPC077").add_supporting_data('user_powerful_priv', [u])
            if p == "SeManageVolumePrivilege":
                report.get_by_id("WPC078").add_supporting_data('user_powerful_priv', [u])
            if p == "SeRelabelPrivilege":
                report.get_by_id("WPC079").add_supporting_data('user_powerful_priv', [u])
            if p == "SeRestorePrivilege":
                report.get_by_id("WPC080").add_supporting_data('user_powerful_priv', [u])
            if p == "SeShutdownPrivilege":
                report.get_by_id("WPC081").add_supporting_data('user_powerful_priv', [u])
            if p == "SeSyncAgentPrivilege":
                report.get_by_id("WPC082").add_supporting_data('user_powerful_priv', [u])
            if p == "SeTakeOwnershipPrivilege":
                report.get_by_id("WPC083").add_supporting_data('user_powerful_priv', [u])
            if p == "SeTcbPrivilege":
                report.get_by_id("WPC084").add_supporting_data('user_powerful_priv', [u])
            if p == "SeTrustedCredManAccessPrivilege":
                report.get_by_id("WPC085").add_supporting_data('user_powerful_priv', [u])


def audit_groups(report):
    grouplist = groups()
    for u in grouplist.get_all():
        #print u.get_fq_name()

        # TODO ignore empty groups
        # TODO consider other privs too
        # TODO remove useless privs
        # TODO More efficient method that doesn't involve looping through all users?  What does secpol.msc do?
        for p in u.get_privileges():
            # print "\t%s" % p
            if p == "SeAssignPrimaryTokenPrivilege":
                report.get_by_id("WPC070").add_supporting_data('group_powerful_priv', [u])
            if p == "SeBackupPrivilege":
                report.get_by_id("WPC071").add_supporting_data('group_powerful_priv', [u])
            if p == "SeCreatePagefilePrivilege":
                report.get_by_id("WPC072").add_supporting_data('group_powerful_priv', [u])
            if p == "SeCreateTokenPrivilege":
                report.get_by_id("WPC073").add_supporting_data('group_powerful_priv', [u])
            if p == "SeDebugPrivilege":
                report.get_by_id("WPC074").add_supporting_data('group_powerful_priv', [u])
            if p == "SeEnableDelegationPrivilege":
                report.get_by_id("WPC075").add_supporting_data('group_powerful_priv', [u])
            if p == "SeLoadDriverPrivilege":
                report.get_by_id("WPC076").add_supporting_data('group_powerful_priv', [u])
            if p == "SeMachineAccountPrivilege":
                report.get_by_id("WPC077").add_supporting_data('group_powerful_priv', [u])
            if p == "SeManageVolumePrivilege":
                report.get_by_id("WPC078").add_supporting_data('group_powerful_priv', [u])
            if p == "SeRelabelPrivilege":
                report.get_by_id("WPC079").add_supporting_data('group_powerful_priv', [u])
            if p == "SeRestorePrivilege":
                report.get_by_id("WPC080").add_supporting_data('group_powerful_priv', [u])
            if p == "SeShutdownPrivilege":
                report.get_by_id("WPC081").add_supporting_data('group_powerful_priv', [u])
            if p == "SeSyncAgentPrivilege":
                report.get_by_id("WPC082").add_supporting_data('group_powerful_priv', [u])
            if p == "SeTakeOwnershipPrivilege":
                report.get_by_id("WPC083").add_supporting_data('group_powerful_priv', [u])
            if p == "SeTcbPrivilege":
                report.get_by_id("WPC084").add_supporting_data('group_powerful_priv', [u])
            if p == "SeTrustedCredManAccessPrivilege":
                report.get_by_id("WPC085").add_supporting_data('group_powerful_priv', [u])


def audit_services(report):
    for s in services().get_services():

        #
        # Check if service runs as a domain/local user
        #
        u = s.get_run_as()
        if len(u.split("\\")) == 2:
            d = u.split("\\")[0]
            if not d in ("NT AUTHORITY", "NT Authority"):
                if d in ("."):
                    # Local account - TODO better way to tell if acct is a local acct?
                    report.get_by_id("WPC064").add_supporting_data('service_domain_user', [s])
                else:
                    # Domain account - TODO better way to tell if acct is a domain acct?
                    report.get_by_id("WPC063").add_supporting_data('service_domain_user', [s])

        if s.get_name() in ("PSEXESVC", "Abel", "fgexec"):
            report.get_by_id("WPC065").add_supporting_data('sectool_services', [s])
        elif s.get_description() in ("PsExec", "Abel", "fgexec"):
            report.get_by_id("WPC065").add_supporting_data('sectool_services', [s])
           
        # TODO check for the presence of files - but not from here 
        #
        # Check if pentest/audit tools have accidentally been left running
        #
        # TODO: psexec
        # disp name = PsExec
        # Desc = blank
        # svc name = PSEXESVC
        # image = C:\WINDOWS\PSEXESVC.EXE
        #
        # TODO: abel
        # disp name = Abel
        # desc = blank
        # svc name = Abel
        # image = C:\WINDOWS\system32\spool\drivers\Abel.exe
        #
        # TODO: fgdump
        # image = %temp%\pwdump.exe
        # %temp%\lsremora.dll fgexec.exe cachedump.exe pstgdump.exe servpw64.exe cachedump64.exe 
        # lsremora64.dll servpw.exe
        # Examine registry key for service
        #
        if s.get_reg_key() and s.get_reg_key().get_sd():

            # Check owner
            if not s.get_reg_key().get_sd().get_owner().is_trusted():
                report.get_by_id("WPC035").add_supporting_data('service_exe_regkey_untrusted_ownership', [s, s.get_reg_key()])

            # Untrusted users can change permissions
            acl = s.get_reg_key().get_issue_acl_for_perms(["WRITE_OWNER", "WRITE_DAC"])
            if acl:
                report.get_by_id("WPC036").add_supporting_data('service_reg_perms', [s, acl])

#            "KEY_SET_VALUE", # GUI "Set Value".  Required to create, delete, or set a registry value.
            acl = s.get_reg_key().get_issue_acl_for_perms(["KEY_SET_VALUE"])
            if acl:
                report.get_by_id("WPC037").add_supporting_data('service_reg_perms', [s, acl])

#            "KEY_CREATE_LINK", # GUI "Create Link".  Reserved for system use.
            acl = s.get_reg_key().get_issue_acl_for_perms(["KEY_CREATE_LINK"])
            if acl:
                report.get_by_id("WPC038").add_supporting_data('service_reg_perms', [s, acl])

#            "KEY_CREATE_SUB_KEY", # GUI "Create subkey"
            acl = s.get_reg_key().get_issue_acl_for_perms(["KEY_CREATE_SUB_KEY"])
            if acl:
                report.get_by_id("WPC039").add_supporting_data('service_reg_perms', [s, acl])

#            "DELETE", # GUI "Delete"
            acl = s.get_reg_key().get_issue_acl_for_perms(["DELETE"])
            if acl:
                report.get_by_id("WPC040").add_supporting_data('service_reg_perms', [s, acl])

            # TODO walk sub keys looking for weak perms - not necessarily a problem, but could be interesting

            pkey = regkey(s.get_reg_key().get_name() + "\Parameters")
            if pkey.is_present():
                v = pkey.get_value("ServiceDll")
                if v:
                    f = File(wpc.utils.env_expand(v))
                    if f.exists():
                        if f.is_replaceable():
                            report.get_by_id("WPC052").add_supporting_data('service_dll', [s, pkey, f])

            # TODO checks on parent keys
            parent = s.get_reg_key().get_parent_key()
            while parent and parent.get_sd():
                # Untrusted user owns parent directory
                if not parent.get_sd().get_owner().is_trusted():
                    report.get_by_id("WPC041").add_supporting_data('service_regkey_parent_untrusted_ownership', [s, parent])

                # Parent dir can have file perms changed
                fa = parent.get_issue_acl_for_perms(["WRITE_OWNER", "WRITE_DAC"])
                if fa:
                    report.get_by_id("WPC042").add_supporting_data('service_regkey_parent_perms', [s, fa])

                # Child allows itself to be delete, parent allows it to be replaced
                fa_parent = parent.get_issue_acl_for_perms(["DELETE"])
                if fa_parent:
                    grandparent = parent.get_parent_key()
                    if grandparent and grandparent.get_sd():
                        # There is no "DELETE_CHILD" type permission within the registry.  Therefore for the delete+replace issue, 
                        # we only have one combination of permissions to look for: the key allows DELETE and the parent allows either 
                        # KEY_CREATE_SUB_KEY or KEY_CREATE_LINK
                        fa_grandparent = grandparent.get_issue_acl_for_perms(["KEY_CREATE_SUB_KEY", "KEY_CREATE_LINK"])
                        if fa_grandparent:
                            report.get_by_id("WPC043").add_supporting_data('service_regkey_parent_grandparent_write_perms', [s, fa_parent, fa_grandparent])

                parent = parent.get_parent_key()

        # Check that the binary name is properly quoted
        if str(s.get_exe_path_clean()).find(" ") > 0: # clean path contains a space
            if str(s.get_exe_path()).find(str('"' + s.get_exe_path_clean()) + '"') < 0: # TODO need regexp.  Could get false positive from this.
                report.get_by_id("WPC051").add_supporting_data('service_info', [s])

        #
        # Examine executable for service
        #
        if s.get_exe_file() and s.get_exe_file().get_sd():

            # Examine parent directories
            parent = s.get_exe_file().get_parent_dir()
            while parent and parent.get_sd():
                # Untrusted user owns parent directory
                if not parent.get_sd().get_owner().is_trusted():
                    report.get_by_id("WPC033").add_supporting_data('service_exe_parent_dir_untrusted_ownership', [s, parent])

                # Parent dir can have file perms changed
                fa = parent.get_file_acl_for_perms(["WRITE_OWNER", "WRITE_DAC"])
                if fa:
                    report.get_by_id("WPC032").add_supporting_data('service_exe_parent_dir_perms', [s, fa])

                # Child allows itself to be delete, parent allows it to be replaced
                fa_parent = parent.get_file_acl_for_perms(["DELETE"])
                if fa_parent:
                    grandparent = parent.get_parent_dir()
                    if grandparent and grandparent.get_sd():
                        fa_grandparent = grandparent.get_file_acl_for_perms(["FILE_ADD_SUBFOLDER"])
                        if fa_grandparent:
                            report.get_by_id("WPC031").add_supporting_data('service_exe_parent_grandparent_write_perms', [s, fa_parent, fa_grandparent])

                # Parent allows child directory to be deleted and replaced
                grandparent = parent.get_parent_dir()
                if grandparent and grandparent.get_sd():
                    fa = grandparent.get_file_acl_for_perms(["FILE_DELETE_CHILD", "FILE_ADD_SUBFOLDER"])
                    if fa:
                        report.get_by_id("WPC030").add_supporting_data('service_exe_parent_dir_perms', [s, fa])

                parent = parent.get_parent_dir()

            # Untrusted user owns exe
            if not s.get_exe_file().get_sd().get_owner().is_trusted():
                report.get_by_id("WPC029").add_supporting_data('service_exe_write_perms', [s])

            # Check if exe can be appended to
            fa = s.get_exe_file().get_file_acl_for_perms(["FILE_APPEND_DATA"])
            if fa:
                report.get_by_id("WPC027").add_supporting_data('service_exe_write_perms', [s, fa])

            # Check if exe can be deleted and perhaps replaced
            fa = s.get_exe_file().get_file_acl_for_perms(["DELETE"])
            if fa:
                # File can be delete (DoS issue)
                report.get_by_id("WPC026").add_supporting_data('service_exe_write_perms', [s, fa])

                # File can be deleted and replaced (privesc issue)
                parent = s.get_exe_file().get_parent_dir()
                if parent and parent.get_sd():
                    fa_parent = parent.get_file_acl_for_perms(["FILE_ADD_FILE"])
                    if fa_parent:
                        report.get_by_id("WPC034").add_supporting_data('service_exe_file_parent_write_perms', [s, fa, fa_parent])

            # Check for file perms allowing overwrite
            fa = s.get_exe_file().get_file_acl_for_perms(["FILE_WRITE_DATA", "WRITE_OWNER", "WRITE_DAC"])
            if fa:
                report.get_by_id("WPC028").add_supporting_data('service_exe_write_perms', [s, fa])

            # TODO write_file on a dir containing an exe might allow a dll to be added
        else:
            if not s.get_exe_file():
                report.get_by_id("WPC062").add_supporting_data('service_no_exe', [s])

        #
        # Examine security descriptor for service
        #
        if s.get_sd():

            # TODO all mine are owned by SYSTEM.  Maybe this issue can never occur!?
            if not s.get_sd().get_owner().is_trusted():
                report.get_by_id("WPC025").add_supporting_data('principals_with_service_ownership', [s, s.get_sd().get_owner()])

            # SERVICE_START
            for a in s.get_sd().get_acelist().get_untrusted().get_aces_with_perms(["SERVICE_START"]).get_aces():
                report.get_by_id("WPC018").add_supporting_data('principals_with_service_perm', [s, a.get_principal()])

            # SERVICE_STOP
            for a in s.get_sd().get_acelist().get_untrusted().get_aces_with_perms(["SERVICE_STOP"]).get_aces():
                report.get_by_id("WPC019").add_supporting_data('principals_with_service_perm', [s, a.get_principal()])

            # SERVICE_PAUSE_CONTINUE
            for a in s.get_sd().get_acelist().get_untrusted().get_aces_with_perms(["SERVICE_PAUSE_CONTINUE"]).get_aces():
                report.get_by_id("WPC020").add_supporting_data('principals_with_service_perm', [s, a.get_principal()])

            # SERVICE_CHANGE_CONFIG
            for a in s.get_sd().get_acelist().get_untrusted().get_aces_with_perms(["SERVICE_CHANGE_CONFIG"]).get_aces():
                report.get_by_id("WPC021").add_supporting_data('principals_with_service_perm', [s, a.get_principal()])

            # DELETE
            for a in s.get_sd().get_acelist().get_untrusted().get_aces_with_perms(["DELETE"]).get_aces():
                report.get_by_id("WPC022").add_supporting_data('principals_with_service_perm', [s, a.get_principal()])

            # WRITE_DAC
            for a in s.get_sd().get_acelist().get_untrusted().get_aces_with_perms(["WRITE_DAC"]).get_aces():
                report.get_by_id("WPC023").add_supporting_data('principals_with_service_perm', [s, a.get_principal()])

            # WRITE_OWNER
            for a in s.get_sd().get_acelist().get_untrusted().get_aces_with_perms(["WRITE_OWNER"]).get_aces():
                report.get_by_id("WPC024").add_supporting_data('principals_with_service_perm', [s, a.get_principal()])


def audit_registry(report):

    #
    # Shell Extensions
    #

    checks = (
        ["Context Menu", "WPC053", "HKLM\Software\Classes\*\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Wow6432Node\Classes\*\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Classes\Folder\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Wow6432Node\Classes\Folder\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Classes\Directory\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Wow6432Node\Classes\Directory\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Classes\AllFileSystemObjects\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Wow6432Node\Classes\AllFileSystemObjects\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Classes\Directory\Background\ShellEx\ContextMenuHandlers"],
        ["Context Menu", "WPC053", "HKLM\Software\Wow6432Node\Classes\Directory\Background\ShellEx\ContextMenuHandlers"],

        ["Property Sheet", "WPC054", "HKLM\Software\Classes\*\ShellEx\PropertySheetHandlers"],
        ["Property Sheet", "WPC054", "HKLM\Software\Wow6432Node\Classes\*\ShellEx\PropertySheetHandlers"],
        ["Property Sheet", "WPC054", "HKLM\Software\Classes\Folder\ShellEx\PropertySheetHandlers"],
        ["Property Sheet", "WPC054", "HKLM\Software\Wow6432Node\Classes\Folder\ShellEx\PropertySheetHandlers"],
        ["Property Sheet", "WPC054", "HKLM\Software\Classes\Directory\Shellex\PropertySheetHandlers"],
        ["Property Sheet", "WPC054", "HKLM\Software\Wow6432Node\Classes\Directory\Shellex\PropertySheetHandlers"],
        ["Property Sheet", "WPC054", "HKLM\Software\Classes\AllFileSystemObjects\ShellEx\PropertySheetHandlers"],
        ["Property Sheet", "WPC054", "HKLM\Software\Wow6432Node\Classes\AllFileSystemObjects\ShellEx\PropertySheetHandlers"],

        ["Copy Hook", "WPC055", "HKLM\Software\Classes\Directory\Shellex\CopyHookHandlers"],
        ["Copy Hook", "WPC055", "HKLM\Software\Wow6432Node\Classes\Directory\Shellex\CopyHookHandlers"],

        ["DragDrop Handler", "WPC056", "HKLM\Software\Classes\Directory\Shellex\DragDropHandlers"],
        ["DragDrop Handler", "WPC056", "HKLM\Software\Wow6432Node\Classes\Directory\Shellex\DragDropHandlers"],
        ["DragDrop Handler", "WPC056", "HKLM\Software\Classes\Folder\ShellEx\DragDropHandlers"],
        ["DragDrop Handler", "WPC056", "HKLM\Software\Wow6432Node\Classes\Folder\ShellEx\DragDropHandlers"],

        ["Column Handler", "WPC057", "HKLM\Software\Classes\Folder\Shellex\ColumnHandlers"],
        ["Column Handler", "WPC057", "HKLM\Software\Wow6432Node\Classes\Folder\Shellex\ColumnHandlers"],
    )

    for check in checks:
        check_type = check[0]
        check_id = check[1]
        check_key = check[2]
        rk = regkey(check_key)
        if rk.is_present:
            for s in rk.get_subkeys():
                # TODO check regkey permissions
                # TODO some of the subkeys are CLSIDs.  We don't process these properly yet.
                clsid = s.get_value("") # This value appears as "(Default)" in regedit
                if clsid:
                    reg_val_files = wpc.utils.lookup_files_for_clsid(clsid)
                    for reg_val_file in reg_val_files:
                        (r, v, f) = reg_val_file
                        # print "[D] regkey: %s, file: %s" % (r.get_name() + "\\" + v, f.get_name())
                        if not f.exists():
                            f = wpc.utils.find_in_path(f)

                        if f and f.is_replaceable():
                            name = s.get_name().split("\\")[-1]
                            report.get_by_id(check_id).add_supporting_data('regkey_ref_replacable_file', [check_type, name, clsid, f, s])

    #
    # Run, RunOnce, RunServices, RunServicesOnce
    #

    runkeys_hklm = (
        [ "WPC058", "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" ],
        [ "WPC058", "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnce" ],
        [ "WPC058", "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Run" ],
        [ "WPC058", "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnce" ],

# TODO RunOnceEx doesn't work like this.  Fix it.  See http://support.microsoft.com/kb/310593/
#        [ "WPC058", "HKLM\Software\Microsoft\Windows\CurrentVersion\RunOnceEx" ],
#        [ "WPC058", "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnceEx" ],

        [ "WPC059", "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunService" ],
        [ "WPC059", "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnceService" ],
        [ "WPC059", "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunService" ],
        [ "WPC059", "HKLM\SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\RunOnceService" ],

    # TODO what about HKCU - trawl for run keys of every single user?
    )

    for runkey_hklm in runkeys_hklm:
        issueid = runkey_hklm[0]
        rk = regkey(runkey_hklm[1])

        if rk.is_present:
            for v in rk.get_values():
                # TODO check regkey permissions
                imagepath = rk.get_value(v)
                if imagepath:
                    f = File(wpc.utils.get_exe_path_clean(imagepath))
                    if f and f.is_replaceable():
                        report.get_by_id(issueid).add_supporting_data('regkey_ref_file', [rk, v, f])

    #
    # KnownDlls
    #

    r = regkey("HKLM\System\CurrentControlSet\Control\Session Manager\KnownDlls")

    dirs = []

    d = r.get_value("DllDirectory")
    if d:
        dirs.append(wpc.utils.env_expand(d))

    d = r.get_value("DllDirectory32")
    if d:
        dirs.append(wpc.utils.env_expand(d))

    if r.is_present() and not dirs == []:
        for v in r.get_values():
            if v == "DllDirectory" or v == "DllDirectory32" or v == "":
                continue

            file_str = r.get_value(v)
            for d in dirs:
                if os.path.exists(d + "\\" + file_str):
                    f = File(d + "\\" + file_str)
                    if f.is_replaceable():
                        report.get_by_id("WPC060").add_supporting_data('regkey_ref_file', [r, v, f])

    #
    # All CLSIDs (experimental)
    #

    results = []
    # Potentially intersting subkeys of clsids are listed here:
    # http://msdn.microsoft.com/en-us/library/windows/desktop/ms691424(v=vs.85).aspx

    # TODO doesn't report files that are not found or check perms of dll passed to rundll32.exe
    # [D] can't find %SystemRoot%\system32\eapa3hst.dll
    # [D] can't find rundll32.exe shell32.dll,SHCreateLocalServerRunDll {601ac3dc-786a-4eb0-bf40-ee3521e70bfb}
    # [D] can't find rundll32.exe C:\WINDOWS\system32\hotplug.dll,CreateLocalServer {783C030F-E948-487D-B35D-94FCF0F0C172}
    # [D] can't find rundll32.exe shell32.dll,SHCreateLocalServerRunDll {995C996E-D918-4a8c-A302-45719A6F4EA7}
    # [D] can't find rundll32.exe shell32.dll,SHCreateLocalServerRunDll {FFB8655F-81B9-4fce-B89C-9A6BA76D13E7}

    r = regkey("HKEY_LOCAL_MACHINE\\SOFTWARE\\Classes\\CLSID")
    for clsid_key in r.get_subkeys():
        # print "[D] Processing clsid %s" % clsid_key.get_name()
        for v in ("InprocServer", "InprocServer32", "LocalServer", "LocalServer32"):
            s = regkey(clsid_key.get_name() + "\\" + v)
            if r.is_present:
                f_str = s.get_value("") # "(Default)" value
                if f_str:
                    f_str_expanded = wpc.utils.env_expand(f_str)
                    f = File(f_str_expanded)
                    if not f.exists():
                        f = wpc.utils.find_in_path(f)

                    if f and f.exists():
                        #print "[D] checking security of %s" % f.get_name()
                        pass
                    else:

                        f_str2 = wpc.utils.get_exe_path_clean(f_str_expanded)
                        if f_str2:
                            f = File(f_str2)
                        else:
                            #might be:
                            #"foo.exe /args"
                            #foo.exe /args
                            f_str2 = f_str.replace("\"", "")
                            f = wpc.utils.find_in_path(File(f_str2))
                            if not f or not f.exists():
                                f_str2 = f_str2.split(" ")[0]
                                f = wpc.utils.find_in_path(File(f_str2))
                                # if f:
                                    # print "[D] how about %s" % f.get_name()
                    if not f:
                        # print "[D] can't find %s" % f_str
                        pass

                    if f and f.is_replaceable():
                        report.get_by_id("WPC061").add_supporting_data('regkey_ref_file', [s, v, f])

    for key_string in wpc.conf.reg_paths:
        #parts = key_string.split("\\")
        #hive = parts[0]
        #key_string = "\\".join(parts[1:])

        r = regkey(key_string)

        if r.get_sd():

            # Check owner
            if not r.get_sd().get_owner().is_trusted():
                report.get_by_id("WPC046").add_supporting_data('regkey_program_untrusted_ownership', [r])

            # Untrusted users can change permissions
            acl = r.get_issue_acl_for_perms(["WRITE_OWNER", "WRITE_DAC"])
            if acl:
                report.get_by_id("WPC047").add_supporting_data('regkey_perms', [r, acl])

#            "KEY_SET_VALUE", # GUI "Set Value".  Required to create, delete, or set a registry value.
            acl = r.get_issue_acl_for_perms(["KEY_SET_VALUE"])
            if acl:
                report.get_by_id("WPC048").add_supporting_data('regkey_perms', [r, acl])

#            "KEY_CREATE_LINK", # GUI "Create Link".  Reserved for system use.
            acl = r.get_issue_acl_for_perms(["KEY_CREATE_LINK", "KEY_CREATE_SUB_KEY"])
            if acl:
                report.get_by_id("WPC049").add_supporting_data('regkey_perms', [r, acl])

#            "DELETE", # GUI "Delete"
            acl = r.get_issue_acl_for_perms(["DELETE"])
            if acl:
                report.get_by_id("WPC050").add_supporting_data('regkey_perms', [r, acl])


# Gather info about files and directories
def audit_program_files(report):
    # Record info about all directories
    include_dirs = 1

    prog_dirs = []
    if os.getenv('ProgramFiles'):
        prog_dirs.append(os.environ['ProgramFiles'])

    if os.getenv('ProgramFiles(x86)'):
        prog_dirs.append(os.environ['ProgramFiles(x86)'])

    for dir in prog_dirs:
        # Walk program files directories looking for executables
        for filename in wpc.utils.dirwalk(dir, wpc.conf.executable_file_extensions, include_dirs):
            f = File(filename)
            # TODO check file owner, parent paths, etc.  Maybe use is_replaceable instead?
            aces = f.get_dangerous_aces()

            for ace in aces:
                if f.is_dir():
                    report.get_by_id("WPC001").add_supporting_data('writable_dirs', [f, ace])
                elif f.is_file():
                    report.get_by_id("WPC001").add_supporting_data('writable_progs', [f, ace])    
                else:
                    print "[E] Ignoring thing that isn't file or directory: " + f.get_name()


def audit_paths(report):
    # TODO other paths too
    # WPC013 - system path
    #audit_path_for_issue(report, p, "WPC013")
    # WPC014 - current user's path
    audit_path_for_issue(report, os.environ["PATH"], "WPC014")
    # WPC015 - users' path
    #audit_path_for_issue(report, p, "WPC015")


def audit_path_for_issue(report, mypath, issueid):
    dirs = set(mypath.split(';'))
    exts = wpc.conf.executable_file_extensions
    for dir in dirs:
        weak_flag = 0
        d = File(dir)
        aces = d.get_dangerous_aces()
        for ace in aces:
            report.get_by_id(issueid).add_supporting_data('writable_dirs', [d, ace])

        for ext in exts:
            for myfile in glob.glob(dir + '\*.' + ext):
                f = File(myfile)
                aces = f.get_dangerous_aces()
                for ace in aces:
                    report.get_by_id(issueid).add_supporting_data('writable_progs', [f, ace])

        # TODO properly check perms with is_replaceable


def section(message):
    print "\n[+] Running: %s" % message
# ------------------------ Main Code Starts Here ---------------------

# Parse command line arguments
options = parseOptions()

# Initialise WPC
# TODO be able to enable/disable caching
wpc.utils.init(options)

# Object to hold all the issues we find
report = report()
wpc.utils.populate_scaninfo(report)
issues = report.get_issues()

# Dump raw data if required
if options.dump_mode:

    if options.do_all or options.do_paths:
        section("dump_paths")
        dump_paths(issues)

    if options.do_all or options.do_eventlogs:
        section("dump_eventlogs")
        dump_eventlogs(issues)

    if options.do_all or options.do_shares:
        section("dump_shares")
        dump_shares(issues)

    if options.do_all or options.do_patches:
        section("dump_patches")
        dump_patches(issues)

    if options.do_all or options.do_loggedin:
        section("dump_loggedin")
        dump_loggedin(issues)

    if options.do_all or options.do_services:
        section("dump_services")
        dump_services(issues)

    if options.do_all or options.do_drivers:
        section("dump_drivers")
        dump_drivers(issues)

    if options.do_all or options.do_processes:
        section("dump_processes")
        dump_processes(issues)

    if options.do_all or options.do_program_files:
        section("dump_program_files")
        dump_program_files(issues)

    if options.do_all or options.do_registry:
        section("dump_registry")
        dump_registry(issues)

    if options.do_all or options.do_users:
        section("dump_users")
        dump_users(issues)

    if options.do_all or options.do_groups:
        section("dump_groups")
        dump_groups(issues)

# Identify security issues
if options.audit_mode:

    if options.do_all or options.do_paths:
        section("audit_paths")
        audit_paths(issues)

    if options.do_all or options.do_eventlogs:
        section("audit_eventlogs")
        audit_eventlogs(issues)

    if options.do_all or options.do_shares:
        section("audit_shares")
        audit_shares(issues)

    if options.do_all or options.do_patches:
        section("audit_patches")
        audit_patches(issues)

    if options.do_all or options.do_loggedin:
        section("audit_loggedin")
        audit_loggedin(issues)

    if options.do_all or options.do_services:
        section("audit_services")
        audit_services(issues)

    if options.do_all or options.do_drivers:
        section("audit_drivers")
        audit_drivers(issues)

    if options.do_all or options.do_processes:
        section("audit_processes")
        audit_processes(issues)

    if options.do_all or options.do_program_files:
        section("audit_program_files")
        audit_program_files(issues)

    if options.do_all or options.do_registry:
        section("audit_registry")
        audit_registry(issues)

    if options.do_all or options.do_users:
        section("audit_users")
        audit_users(issues)

    if options.do_all or options.do_groups:
        section("audit_groups")
        audit_groups(issues)

    if options.report_file_stem:
        # Don't expose XML to users as format will change shortly
        # filename = "%s.xml" % options.report_file_stem
        # print "[+] Saving report file %s" % filename
        # f = open(filename, 'w')
        # f.write(report.as_xml_string())
        # f.close()

        filename = "%s.html" % options.report_file_stem
        print "[+] Saving report file %s" % filename
        f = open(filename, 'w')
        f.write(report.as_html())
        f.close()

        filename = "%s.txt" % options.report_file_stem
        print "[+] Saving report file %s" % filename
        f = open(filename, 'w')
        f.write(report.as_text())
        f.close()

    #wpc.conf.cache.print_stats()