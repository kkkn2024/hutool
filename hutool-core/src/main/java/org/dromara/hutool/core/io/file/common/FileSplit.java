package org.dromara.hutool.core.io.file.common;

import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.Comparator;
import java.util.stream.Stream;

/**
 * file split and merge util
 */
public class FileSplit {
    private static final int SPLIT_DEFAULT_SIZE_BYTE = 10 * 1024 * 1024; // default 10MB

    /*
         args[0]; // -s split; -m merge
            -s
           FileSplit -s file outputDir   // default 10MB
           FileSplit -s file outputDir 1M    // 1MB
           FileSplit -s file outputDir 1K  // 1KB
           FileSplit -s file outputDir 1024  // 1KB

            -m
           FileSplit -m mergeDir outputFilePath
     */
    public static void main(String[] args) {
        System.out.println("args = " + Arrays.toString(args));
        String op = args[0]; // -s split; -m merge
        if (!"-s".equals(op) && !"-m".equals(op)) {
            System.err.println("-s split; -m merge");
            return;
        }
        if (op.equals("-s")) {
            doSplit(args);
        } else {
            doMerge(args);
        }
    }

    private static void doMerge(String[] args) {
        String mergeDirPath = args[1];
        String outputFilePath = args[2];
        File mergeDir = new File(mergeDirPath);
        File[] files = mergeDir.listFiles();
        assert files != null;
        System.out.println("start merging " + files.length + " files");
        try (FileOutputStream fos = new FileOutputStream(outputFilePath)) {
            Stream.of(files)
                    .sorted(Comparator.comparing(File::getName))
                    .forEach(file -> {
                        try {
                            byte[] bytes = Files.readAllBytes(file.toPath());
                            fos.write(bytes);
                            System.out.println("merged " + file.getName());
                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    });

        } catch (IOException e) {
            e.printStackTrace();
        }
    }

    private static void doSplit(String[] args) {
        String splitFilePath = args[1];
        String outputDir = args[2];
        int splitSizeByte = SPLIT_DEFAULT_SIZE_BYTE;
        if (args.length > 3) {
            String splitSize = args[3];
            if (splitSize.endsWith("M")) {
                splitSize = splitSize.replace("M", "");
                splitSizeByte = Integer.parseInt(splitSize) * 1024 * 1024;
            } else if (splitSize.endsWith("K")) {
                splitSize = splitSize.replace("K", "");
                splitSizeByte = Integer.parseInt(splitSize) * 1024;
            } else {
                splitSizeByte = Integer.parseInt(splitSize);
            }
        }

        File splitFile = new File(splitFilePath);
        if (!splitFile.exists()) {
            throw new IllegalArgumentException("splitFilePath not found: " + splitFilePath);
        }
        File outDir = new File(outputDir);
        if (!outDir.exists() || !outDir.isDirectory()) {
            throw new IllegalArgumentException("outputDir not found or is not dir: " + outputDir);
        }
        if (outDir.listFiles() != null && outDir.listFiles().length > 0) {
            throw new IllegalArgumentException("outputDir contains files: " + outputDir);
        }
        try (FileInputStream fis = new FileInputStream(splitFile)) {
            byte[] buffer = new byte[splitSizeByte];
            int len;
            int fileCount = 0;
            while ((len = fis.read(buffer)) != -1) {
                File targetFile = new File(outDir, getStrWith3Len(fileCount) + ".bin");
                try (FileOutputStream fos = new FileOutputStream(targetFile)) {
                    System.out.println("split file: " + targetFile.getName());
                    ++fileCount;
                    fos.write(buffer, 0, len);
                }
            }
            System.out.println("split files count: " + fileCount);
        } catch (IOException e) {
            throw new RuntimeException(e);
        }
    }

    static String getStrWith3Len(int n) {
        if (n >= 100) {
            return String.valueOf(n);
        }
        if (n >= 10) {
            return "0" + n;
        }
        return "00" + n;
    }
}
