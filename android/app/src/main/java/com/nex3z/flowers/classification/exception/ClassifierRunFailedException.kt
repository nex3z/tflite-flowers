package com.nex3z.flowers.classification.exception

class ClassifierRunFailedException(
    cause: Throwable
) : BaseException(
    CODE_CLASSIFIER_RUN_FAILED,
    "Failed to initialize classifier",
    cause
)
