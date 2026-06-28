#!/usr/bin/env pwsh
#REQUIRES -Version 6

<#
.SYNOPSIS
    A stand-alone PowerShell script to make Batch Predictions against a deployment.
.DESCRIPTION
    Usage:
    batch_prediction.ps1 <input_file> <output_file> <deployment_id> <api_key> [args]

    Otherwise see SYNTAX in the help menu.

    NOTE! Please run this script using Powershell Core 6 or higher.
.LINK
    Read more at:
    https://app.datarobot.com/docs/predictions/batch/batch-prediction-api/index.html
.EXAMPLE
    For help, run:
    batch_prediction.ps1 -?
.EXAMPLE
    .\batch_prediction.ps1 \
    -input_file <input_file.csv> \
    -output_file <output_file.csv> \
    -deployment_id <deployment_id> \
    -app_host https://app.datarobot.com \
    -api_key <api_key>
#>

Param(
    [Parameter(
        Mandatory=$true,
        Position=0,
        HelpMessage="Input CSV file with data to be scored.")
    ]
    [String]$input_file,

    [Parameter(
        Mandatory=$true,
        Position=1,
        HelpMessage="Output CSV file with the scored data.")
    ]
    [String]$output_file,

    [Parameter(
        Mandatory=$true,
        Position=2,
        HelpMessage="Specifies the model deployment identification string.")
    ]
    [String]$deployment_id,

    [Parameter(
        HelpMessage="Specifies the protocol (http or https) and hostname of the public API endpoint. E.g. 'https://your-domain.datarobot.com'")
    ]
    [String]$app_host = "https://app.datarobot.com",

    [Parameter(
        Mandatory=$true,
        HelpMessage="Specifies the api token for the requests.")
    ]
    [String]$api_key,

    [Parameter(
        HelpMessage="Specifies the number of concurrent requests to submit. (default: 4)")
    ]
    [Int]$n_concurrent = 4,

    [Parameter(
        HelpMessage=("Specifies the path to a CA_BUNDLE file or directory with " +
                     "certificates of trusted Certificate Authorities (CAs) to " +
                     "be used for SSL verification. By default the system's set " +
                     "of trusted certificates will be used."))
    ]
    [String]$ca_bundle,

    [Parameter(
        HelpMessage=("Skip SSL certificates verification for HTTPS endpoints. " +
                     "Using this flag will cause the argument for ca_bundle to be ignored."))
    ]
    [switch]$insecure = $FALSE,

    [Parameter(
        HelpMessage=("The maximum number of prediction explanations that will be " +
                     "generate for each prediction. Not compatible with api version api/v1"))
    ]
    [Int]$max_prediction_explanations,

    [Parameter(
        HelpMessage=("The maximum number of text ngram prediction explanations that will be " +
                     "generated for each prediction. Set to 'all' to obtain all the ngram alias
                     explanations or set to a positive integer value"))
    ]
    [Int]$max_ngram_explanations,

    [Parameter(
        HelpMessage=("Number of top predicted classes for each row that will be explained. " +
                     "Only for clustering and multiclass explanations."))
    ]
    [Int]$explanation_num_top_classes,

    [Parameter(
        HelpMessage=("List of class names that will be explained for each row. " +
                     "Only for clustering and multiclass explanations."))
    ]
    [String[]]$explanation_class_names,

    [Parameter(
        HelpMessage=("Set the timeout value in seconds for the up- and download connections " +
        "(default: 600 seconds, meaning 10 minutes)"))
    ]
    [Int]$timeout = 600,

    [Parameter(
        HelpMessage="Specifies the column names to append to the predictions. Enter as a comma-separated list.")
    ]
    [String[]]$passthrough_columns,

    [Parameter(
        HelpMessage="Append all columns to result from scoring dataset.")
    ]
    [switch]$passthrough_columns_set = $false,

    [Parameter(
        HelpMessage="Exclude probabilities and threashold for all classes.")
    ]
    [switch]$exclude_probabilities = $false,

    [Parameter(
        HelpMessage="Include only probabilities for classes listed in the given array.")
    ]
    [String[]]$include_probabilities_classes,

    [Parameter(
        HelpMessage="Include 'prediction_status' column in the output.")
    ]
    [switch]$include_prediction_status = $false,

    [Parameter(
        HelpMessage=("A mapping of columns to rename from/to. Set a target column empty " +
                     "to ignore it; Has next format: columns_1=columns_r_1,columns_2=column_r_2,columns_3="))
    ]
    [hashtable]$column_names_remapping,

    [Parameter(
        HelpMessage=("Declare the dataset encoding. If an encoding is not provided the " +
                     "batch_scoring script attempts to detect it. E.g 'utf-8', 'latin-1' or " +
                     "'iso2022_jp'. See the Python docs for a list of valid encodings " +
                     "https://docs.python.org/3/library/codecs.html#standard-encodings'"))
    ]
    [String]$encoding,

    [Parameter(
        HelpMessage=("The delimiter character to use. Default: , (comma). " +
                     "To specify TAB as a delimiter, use the string tab"))
    ]
    [String]$delimiter,

    [Parameter(
        HelpMessage=("The character to use for quoting fields containing the delimiter. " +
                     "If not specified, the Batch Predictions API will use "))
    ]
    [String]$quotechar,

    [Parameter(
        HelpMessage=("[DEPRECATED] Specifies column name for prediction results, empty name " +
                     "is used if not specified. For binary predictions assumes last class in lexical order as positive"))
    ]
    [String]$pred_name,

    [Parameter(
        HelpMessage=("[DEPRECATED] Specifies column name for prediction threshold for binary classification. " +
                     "Column will not be included if not specified"))
    ]
    [String]$pred_threshold,

    [Parameter(
        HelpMessage=("[DEPRECATED] Specifies column name for prediction decision, the value predicted " +
                     "by the model (class label for classification)"))
    ]
    [String]$pred_decision,

    [Parameter(
        HelpMessage="Prefix for batch name that will be used for tracking predictions")
    ]
    [String]$batch_prefix,

    [Parameter(
        HelpMessage="The forecast point, use 'infer' to infer from dataset")
    ]
    [String]$forecast_point,

    [Parameter(
        HelpMessage="Start date for historical predictions")
    ]
    [String]$predictions_start_date,

    [Parameter(
        HelpMessage="End date for historical predictions")
    ]
    [String]$predictions_end_date
)

if (-Not $app_host.StartsWith("http://") -And -Not $app_host.StartsWith("https://")) {
  Write-Host "Please prefix a protocol (either http:// or https://) to your app_host ($app_host"
  return
}

if (-Not $app_host.StartsWith("https://") -And -Not $insecure) {
  Write-Host "When predicting against a non-secure endpoint (http://$app_host) you must supply the parameter -insecure to the command."
  return
}

Set-Variable CHUNK_SIZE -option Constant -value ([int]16384)

function Get-Rest-Parameters {
  $rest_parameters = @{
    TimeoutSec = $timeout
    Authentication = "Bearer"
    Token = (ConvertTo-SecureString -String $api_key -AsPlainText -Force)
    UserAgent = "IntegrationSnippet-StandAlone-Powershell"
  }

  if ($insecure) {
    $rest_parameters["SkipCertificateCheck"] = $true
    $rest_parameters["AllowUnencryptedAuthentication"] = $true
  }

  if ($ca_bundle) {
    $rest_parameters["Certificate"] = $ca_bundle
  }

  return $rest_parameters
}

$UploadBatchPredictionDataJob = {
  param ($timeout, $api_key, $upload_link, $input_file, $chunk_size)

  $webRequest = [System.Net.HttpWebRequest]::Create($upload_link)
  $webRequest.Method = "PUT"
  $webRequest.Timeout = $timeout * 1000
  $webRequest.ContentType = "text/csv; encoding=utf-8"
  $webRequest.Headers.Add("Authorization", "Bearer $api_key")

  $file_length = ([System.IO.FileInfo]$input_file).Length
  $webRequest.ContentLength = $file_length
  $webRequest.AllowWriteStreamBuffering=$false

  $requestStream = $webRequest.GetRequestStream()
  $fileStream = [System.IO.File]::OpenRead($input_file)
  $chunk = New-Object byte[] $chunk_size
  while( $bytesRead = $fileStream.Read($chunk, 0, $chunk_size) )
  {
    $requestStream.write($chunk, 0, $bytesRead)
    $requestStream.Flush()
  }

  $webRequest.GetResponse()
  $FileStream.Close()
  $requestStream.Close()
}

$DownloadBatchPredictionOutputJob = {
  param ($timeout, $insecure, $ca_bundle, $api_key, $self_link, $output_file, $chunk_size)

  $rest_parameters = @{
    Method = "GET"
    Uri = $self_link
    TimeoutSec = $timeout
    Authentication = "Bearer"
    Token = (ConvertTo-SecureString -String $api_key -AsPlainText -Force)
    UserAgent = "IntegrationSnippet-StandAlone-Powershell"
  }

  if ($insecure) {
    $rest_parameters["SkipCertificateCheck"] = $true
    $rest_parameters["AllowUnencryptedAuthentication"] = $true
  }

  if ($ca_bundle) {
    $rest_parameters["Certificate"] = $ca_bundle
  }

  $status = "INITIALIZING"
  While ($status -eq "INITIALIZING") {
    $prediction_job = Invoke-RestMethod @rest_parameters
    $status = $prediction_job.status
    Start-Sleep -s 1
  }

  $webRequest = [System.Net.HttpWebRequest]::Create($prediction_job.links.download)
  $webRequest.Method = "GET"
  $webRequest.Timeout = $timeout * 1000
  $webRequest.Headers.Add("Authorization", "Bearer $api_key")
  $webRequest.ContentType = "text/csv; encoding=utf-8"
  $webRequest.AllowReadStreamBuffering = $false

  $fileStream = [System.IO.File]::OpenWrite($output_file)
  $responseStream = $webRequest.GetResponse().GetResponseStream()

  $chunk = New-Object byte[] $chunk_size
  while( $bytesRead = $responseStream.Read($chunk, 0, $chunk_size) )
  {
    $fileStream.write($chunk, 0, $bytesRead)
    $responseStream.Flush()
  }

  $fileStream.Close()
  $responseStream.Close()
}

function Make-DataRobot-Batch-Prediction {
  param ($input_file, $output_file, $payload)
  $headers = @{
    "Content-Type" = "application/json; encoding=utf-8"
  }

  $rest_parameters = Get-Rest-Parameters

  # Create job
  $prediction_job = Invoke-RestMethod @rest_parameters -Uri "$app_host/api/v2/batchPredictions/" -Method Post -Headers $headers -Body $payload

  $job_id = $prediction_job.id
  $links = $prediction_job.links
  $intake = $prediction_job.jobSpec.intakeSettings.type
  $output = $prediction_job.jobSpec.outputSettings.type
  $queue_position = $prediction_job.queuePosition
  $self_link = $links.self

  if ($null -eq $self_link) {
    write-host "Variable \$self_link is empty. Possibly because \$prediction_job.links is: $prediction_job"
    Exit
  }

  $upload_link = $links.csvUpload

  write-host "Created Batch Prediction job ID $job_id for deployment ID $deployment_id
              ($intake -> $output) on $self_link queue position $queue_position."

  # Run simultaneously upload and download
  # These are separate PowerShell processes, so only what is passed as arguments is accessible from inside these functions
  $upload_job = Start-Job -ScriptBlock $UploadBatchPredictionDataJob -ArgumentList $timeout, $api_key, $upload_link, $input_file, $CHUNK_SIZE
  $download_job = Start-Job -ScriptBlock $DownloadBatchPredictionOutputJob -ArgumentList $timeout, $insecure, $ca_bundle, $api_key, $self_link, $output_file, $CHUNK_SIZE

  While ($true) {
    $prediction_job = Invoke-RestMethod @rest_parameters -Uri $self_link -Method Get -Headers $headers

    $status = $prediction_job.status
    if ($status -eq "INITIALIZING") {
        $queue_position = $prediction_job.queuePosition

        if ($queue_position -gt 0) {
            write-host "Waiting for $queue_position s to complete..."
        } else {
            write-host "Waiting for a queue position..."
        }

        Start-Sleep -s 10
        Continue
    }

    if ($status -eq "RUNNING") {
        write-host "Waiting for the job to complete:" $prediction_job.percentageCompleted
        write-host "Number of scored rows:" $prediction_job.scoredRows
        write-host "Number of failed rows:" $prediction_job.failedRows
        write-host "Number of skipped rows:" $prediction_job.skippedRows

        Start-Sleep -s 10
        Continue
    }

    if ($status -eq "COMPLETED") {
        $download_job | Wait-Job | Out-Null
        $upload_job | Wait-Job | Out-Null

        write-host "Waiting for the job to complete: 100%"
        write-host "Number of scored rows:" $prediction_job.scoredRows
        write-host "Number of failed rows:" $prediction_job.failedRows
        write-host "Number of skipped rows:" $prediction_job.skippedRows
        write-host "Results downloaded to:" $output_file

        # Procesamiento de recomendaciones saludables
        Write-Host "Generando recomendaciones saludables..."
        $results = Import-Csv -Path $output_file
        foreach ($row in $results) {
            $score = [double]$row.prediction 
            $recomendacion = if ($score -gt 0.7) { 
                "Riesgo ALTO: Consulte a un cardiólogo urgentemente, reduzca sodio y grasas saturadas." 
            } elseif ($score -gt 0.4) { 
                "Riesgo MODERADO: Inicie actividad física regular y mejore su dieta." 
            } else { 
                "Riesgo BAJO: Mantenga hábitos saludables y chequeos anuales." 
            }
            $row | Add-Member -MemberType NoteProperty -Name "Recomendacion" -Value $recomendacion
        }
        $results | Export-Csv -Path $output_file -NoTypeInformation
        Write-Host "Recomendaciones agregadas al archivo."

        return
    }

    if ($status -eq "ABORTED" -Or $status -eq "FAILED") {
        write-host "Job was aborted"
        return
    }
  }
}

$payload = @{
    'deploymentId' = $deployment_id
}

# Number of simultaneous requests
if ($n_concurrent) {
    $payload['numConcurrent'] = $n_concurrent
}

# Set max prediction explanations
if ($max_prediction_explanations) {
    $payload['maxExplanations'] = $max_prediction_explanations
}
if ($max_ngram_explanations) {
    $payload['maxNgramExplanations'] = $max_ngram_explanations
}

# Configure multiclass explanations mode
if ($explanation_num_top_classes) {
    $payload['explanationNumTopClasses'] = $explanation_num_top_classes
}

if ($explanation_class_names) {
    $payload['explanationClassNames'] = $explanation_class_names
}

# Set passthrough columns
if ($passthrough_columns) {
    $payload['passthroughColumns'] = $passthrough_columns
}

# Include all passthrough columns into result
if ($passthrough_columns_set) {
    $payload['passthroughColumnsSet'] = 'all'
}

# Exclude probabilities
if ($exclude_probabilities) {
    $payload['includeProbabilities'] = $False
}

# Include only specific classes
if ($include_probabilities_classes) {
    $payload['includeProbabilities'] = False
    $payload['includeProbabilitiesClasses'] = $include_probabilities_classes
}

# Include prediction_status column
if ($include_prediction_status) {
    $payload['includePredictionStatus'] = $True
}

# Columns name remapping
if ($column_names_remapping) {
    $payload['columnNamesRemapping'] = $column_names_remapping
}
# Batch monitoring
if ($batch_prefix) {
    $payload['monitoringBatchPrefix'] = $batch_prefix
}
# Set csv settings
$csv_settings = @{}
if ($encoding) {
    $csv_settings['encoding'] = $encoding
}
if ($delimiter) {
    $csv_settings['delimiter'] = $delimiter
}
if ($quotechar) {
    $csv_settings['quotechar'] = $quotechar
}
if ($csv_settings.Count -ne 0) {
    write-host $csv_settings
    $payload['csvSettings'] = $csv_settings
}

# Set TS settings
if ($forecast_point) {
    $payload['timeseriesSettings'] = @{}
    $payload['timeseriesSettings']['type'] = 'forecast'
    if ($forecast_point -ne 'infer') {
        $payload['timeseriesSettings']['forecastPoint'] = $forecast_point
    }
} elseif ($predictions_start_date -and $predictions_end_date) {
    $payload['timeseriesSettings'] = @{}
    $payload['timeseriesSettings']['type'] = 'historical'
    $payload['timeseriesSettings']['predictionsStartDate'] = $predictions_start_date
    $payload['timeseriesSettings']['predictionsEndDate'] = $predictions_end_date
} elseif ($predictions_start_date) {
    write-host "Cannot use --predictions_start_date without --predictions_end_date"
    Exit
} elseif ($predictions_end_date) {
    write-host "Cannot use --predictions_end_date without --predictions_start_date"
    Exit
}

$payload = $payload | ConvertTo-Json

Make-DataRobot-Batch-Prediction $input_file $output_file $payload
