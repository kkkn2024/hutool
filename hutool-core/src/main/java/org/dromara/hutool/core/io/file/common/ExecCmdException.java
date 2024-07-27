package org.dromara.hutool.core.io.file.common;

public class ExecCmdException extends Exception {
    public ExecCmdException(String msg) {
        super(msg);
    }

    public ExecCmdException(Exception e) {
        super(e);
    }

    public ExecCmdException(String msgTemplate, Object ...params) {
        super(String.format(msgTemplate, params));
    }
}
