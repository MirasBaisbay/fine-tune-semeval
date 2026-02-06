# Evaluation Report

**Total Processed:** 18
**Successful:** 14
**Failed:** 4

## Performance Metrics

| Metric | Accuracy |
|--------|----------|
| **Bias Label** | 28.57% |
| **Factuality Label** | 35.71% |

## Detailed Bias Report
```text
               precision    recall  f1-score   support

       Center       0.50      0.57      0.53         7
 Extreme Left       0.00      0.00      0.00         0
  Left-Center       0.00      0.00      0.00         2
Pseudoscience       0.00      0.00      0.00         1
        Right       0.00      0.00      0.00         2
 Right-Center       0.00      0.00      0.00         2

     accuracy                           0.29        14
    macro avg       0.08      0.10      0.09        14
 weighted avg       0.25      0.29      0.27        14

```

## Detailed Factuality Report
```text
              precision    recall  f1-score   support

        High       0.38      0.50      0.43         6
         Low       0.00      0.00      0.00         0
       Mixed       1.00      0.29      0.44         7
   Very High       0.00      0.00      0.00         1

    accuracy                           0.36        14
   macro avg       0.34      0.20      0.22        14
weighted avg       0.66      0.36      0.41        14

```

## Mismatches
- **OpsLens**
  - Bias: GT `Right` vs Sys `Pseudoscience`
  - Fact: GT `Mixed` vs Sys `High`
- **OpenVaers**
  - Bias: GT `Right` vs Sys `Pseudoscience`
  - Fact: GT `Mixed` vs Sys `High`
- **Open to Debate**
  - Fact: GT `High` vs Sys `Very High`
- **Open Doors**
  - Bias: GT `Right-Center` vs Sys `Extreme Left`
  - Fact: GT `Mixed` vs Sys `High`
- **Open**
  - Bias: GT `Center` vs Sys `Pseudoscience`
- **Onslow News**
  - Bias: GT `Right-Center` vs Sys `Center`
  - Fact: GT `Mixed` vs Sys `High`
- **Online Updates**
  - Bias: GT `Pseudoscience` vs Sys `Center`
  - Fact: GT `Mixed` vs Sys `Low`
- **Amber Integrated**
  - Bias: GT `Left-Center` vs Sys `Center`
  - Fact: GT `High` vs Sys `Low`
- **ABT Associates**
  - Bias: GT `Left-Center` vs Sys `Center`
- **ABC News/Washington Post Polling**
  - Fact: GT `Very High` vs Sys `High`
- **270toWin**
  - Fact: GT `High` vs Sys `Low`
- **Health Insider**
  - Bias: GT `Center` vs Sys `Pseudoscience`
- **20/20 Insight**
  - Bias: GT `Center` vs Sys `Extreme Left`
