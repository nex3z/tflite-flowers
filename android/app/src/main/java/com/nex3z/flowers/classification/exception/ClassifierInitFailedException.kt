package com.nex3z.flowers.classification.exception

class ClassifierInitFailedException(
    cause: Throwable
) : BaseException(
    CODE_CLASSIFIER_INIT_FAILED,
    "Failed to initialize classifier",
    cause
)
