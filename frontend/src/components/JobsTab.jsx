import {
  Briefcase,
  Building2,
  Calendar,
  ExternalLink,
  Filter,
  MapPin,
  Search,
  Tag,
  Trash2,
} from "lucide-react";
import React, { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "react-query";
import { deleteJob, getJob, getJobs, searchJobs } from "../services/api";

const JobsTab = () => {
  const [selectedJob, setSelectedJob] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [filters, setFilters] = useState({
    company: "",
    location: "",
    working_type: "",
  });
  const [showFilters, setShowFilters] = useState(false);
  const queryClient = useQueryClient();

  // Fetch jobs with filters
  const {
    data: jobs = [],
    isLoading: jobsLoading,
    error,
  } = useQuery(["jobs", filters], () => getJobs(filters), {
    keepPreviousData: true,
  });

  // Search jobs
  const { data: searchResults = [], isLoading: searchLoading } = useQuery(
    ["jobs-search", searchQuery],
    () => searchJobs(searchQuery),
    {
      enabled: searchQuery.length > 2,
      keepPreviousData: true,
    }
  );

  const deleteJobMutation = useMutation(deleteJob, {
    onSuccess: () => {
      queryClient.invalidateQueries("jobs");
      queryClient.invalidateQueries("jobs-search");
      if (selectedJob) {
        setSelectedJob(null);
      }
    },
  });

  const handleJobSelect = async (jobId) => {
    try {
      const job = await getJob(jobId);
      setSelectedJob(job);
    } catch (error) {
      console.error("Error fetching job details:", error);
    }
  };

  const handleDeleteJob = (jobId, event) => {
    event.stopPropagation();
    if (window.confirm("Are you sure you want to delete this job?")) {
      deleteJobMutation.mutate(jobId);
    }
  };

  const handleFilterChange = (key, value) => {
    setFilters((prev) => ({ ...prev, [key]: value }));
  };

  const clearFilters = () => {
    setFilters({ company: "", location: "", working_type: "" });
  };

  const displayJobs = searchQuery.length > 2 ? searchResults : jobs;
  const isLoading = searchQuery.length > 2 ? searchLoading : jobsLoading;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm border p-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center">
              <Briefcase className="h-6 w-6 mr-2 text-purple-600" />
              Job Management
            </h2>
            <p className="text-gray-600 mt-1">
              Manage and explore job postings
            </p>
          </div>
          <div className="text-sm text-gray-500">
            {displayJobs.length} job{displayJobs.length !== 1 ? "s" : ""} found
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Left Panel - Job List (60%) */}
        <div className="lg:col-span-3 space-y-4">
          {/* Search and Filters */}
          <div className="bg-white rounded-lg shadow-sm border p-4">
            <div className="flex flex-col sm:flex-row gap-4">
              {/* Search */}
              <div className="flex-1">
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search jobs by position, company, or location..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  />
                </div>
              </div>

              {/* Filter Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 focus:ring-2 focus:ring-purple-500 focus:border-transparent"
              >
                <Filter className="h-4 w-4 mr-2" />
                Filters
              </button>
            </div>

            {/* Filters */}
            {showFilters && (
              <div className="mt-4 pt-4 border-t border-gray-200">
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Company
                    </label>
                    <input
                      type="text"
                      placeholder="Filter by company"
                      value={filters.company}
                      onChange={(e) =>
                        handleFilterChange("company", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Location
                    </label>
                    <input
                      type="text"
                      placeholder="Filter by location"
                      value={filters.location}
                      onChange={(e) =>
                        handleFilterChange("location", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Working Type
                    </label>
                    <select
                      value={filters.working_type}
                      onChange={(e) =>
                        handleFilterChange("working_type", e.target.value)
                      }
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    >
                      <option value="">All Types</option>
                      <option value="Full-time">Full-time</option>
                      <option value="Part-time">Part-time</option>
                      <option value="Contract">Contract</option>
                      <option value="Remote">Remote</option>
                    </select>
                  </div>
                </div>
                <div className="mt-4 flex justify-end">
                  <button
                    onClick={clearFilters}
                    className="px-4 py-2 text-sm text-gray-600 hover:text-gray-800"
                  >
                    Clear Filters
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Job List */}
          <div className="bg-white rounded-lg shadow-sm border">
            {isLoading ? (
              <div className="p-8 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                <p className="text-gray-600 mt-2">Loading jobs...</p>
              </div>
            ) : error ? (
              <div className="p-8 text-center">
                <p className="text-red-600">
                  Error loading jobs: {error.message}
                </p>
              </div>
            ) : displayJobs.length === 0 ? (
              <div className="p-8 text-center">
                <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-600">No jobs found</p>
                {searchQuery && (
                  <p className="text-sm text-gray-500 mt-1">
                    Try adjusting your search or filters
                  </p>
                )}
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {displayJobs.map((job) => (
                  <div
                    key={job.id}
                    onClick={() => handleJobSelect(job.id)}
                    className={`p-4 hover:bg-gray-50 cursor-pointer transition-colors ${
                      selectedJob?.id === job.id
                        ? "bg-purple-50 border-l-4 border-purple-500"
                        : ""
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <h3 className="text-lg font-semibold text-gray-900">
                            {job.position}
                          </h3>
                          {job.working_type && (
                            <span className="px-2 py-1 text-xs font-medium bg-blue-100 text-blue-800 rounded-full">
                              {job.working_type}
                            </span>
                          )}
                        </div>

                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-2">
                          <div className="flex items-center gap-1">
                            <Building2 className="h-4 w-4" />
                            {job.company}
                          </div>
                          {job.location && (
                            <div className="flex items-center gap-1">
                              <MapPin className="h-4 w-4" />
                              {job.location}
                            </div>
                          )}
                          {job.created_at && (
                            <div className="flex items-center gap-1">
                              <Calendar className="h-4 w-4" />
                              {new Date(job.created_at).toLocaleDateString()}
                            </div>
                          )}
                        </div>

                        {job.tags && job.tags.length > 0 && (
                          <div className="flex flex-wrap gap-1">
                            {job.tags.slice(0, 5).map((tag, index) => (
                              <span
                                key={index}
                                className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full"
                              >
                                <Tag className="h-3 w-3 mr-1" />
                                {tag}
                              </span>
                            ))}
                            {job.tags.length > 5 && (
                              <span className="text-xs text-gray-500">
                                +{job.tags.length - 5} more
                              </span>
                            )}
                          </div>
                        )}
                      </div>

                      <div className="flex items-center gap-2 ml-4">
                        {job.job_link && (
                          <a
                            href={job.job_link}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={(e) => e.stopPropagation()}
                            className="p-2 text-gray-400 hover:text-purple-600 transition-colors"
                            title="View original job posting"
                          >
                            <ExternalLink className="h-4 w-4" />
                          </a>
                        )}
                        <button
                          onClick={(e) => handleDeleteJob(job.id, e)}
                          disabled={deleteJobMutation.isLoading}
                          className="p-2 text-gray-400 hover:text-red-600 transition-colors disabled:opacity-50"
                          title="Delete job"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Job Details (40%) */}
        <div className="lg:col-span-2">
          {selectedJob ? (
            <div className="bg-white rounded-lg shadow-sm border p-6 sticky top-4">
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-xl font-bold text-gray-900">Job Details</h3>
                {selectedJob.job_link && (
                  <a
                    href={selectedJob.job_link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="flex items-center text-sm text-purple-600 hover:text-purple-700"
                  >
                    <ExternalLink className="h-4 w-4 mr-1" />
                    View Original
                  </a>
                )}
              </div>

              <div className="space-y-4">
                {/* Basic Info */}
                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Position</h4>
                  <p className="text-gray-700">{selectedJob.position}</p>
                </div>

                <div>
                  <h4 className="font-semibold text-gray-900 mb-2">Company</h4>
                  <p className="text-gray-700">{selectedJob.company}</p>
                </div>

                {selectedJob.location && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Location
                    </h4>
                    <p className="text-gray-700">{selectedJob.location}</p>
                  </div>
                )}

                {selectedJob.working_type && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Working Type
                    </h4>
                    <p className="text-gray-700">{selectedJob.working_type}</p>
                  </div>
                )}

                {selectedJob.company_size && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Company Size
                    </h4>
                    <p className="text-gray-700">{selectedJob.company_size}</p>
                  </div>
                )}

                {/* Skills */}
                {selectedJob.skills && selectedJob.skills.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Skills</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedJob.skills.map((skill, index) => (
                        <span
                          key={index}
                          className="px-2 py-1 text-sm bg-blue-100 text-blue-800 rounded-full"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Technical Skills */}
                {selectedJob.technical_skills &&
                  selectedJob.technical_skills.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">
                        Technical Skills
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {selectedJob.technical_skills.map((skill, index) => (
                          <span
                            key={index}
                            className="px-2 py-1 text-sm bg-green-100 text-green-800 rounded-full"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                {/* Responsibilities */}
                {selectedJob.responsibilities &&
                  selectedJob.responsibilities.length > 0 && (
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-2">
                        Responsibilities
                      </h4>
                      <ul className="list-disc list-inside space-y-1 text-gray-700">
                        {selectedJob.responsibilities.map(
                          (responsibility, index) => (
                            <li key={index}>{responsibility}</li>
                          )
                        )}
                      </ul>
                    </div>
                  )}

                {/* Benefits */}
                {selectedJob.benefits && selectedJob.benefits.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Benefits
                    </h4>
                    <ul className="list-disc list-inside space-y-1 text-gray-700">
                      {selectedJob.benefits.map((benefit, index) => (
                        <li key={index}>{benefit}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Tags */}
                {selectedJob.tags && selectedJob.tags.length > 0 && (
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-2">Tags</h4>
                    <div className="flex flex-wrap gap-2">
                      {selectedJob.tags.map((tag, index) => (
                        <span
                          key={index}
                          className="inline-flex items-center px-2 py-1 text-xs font-medium bg-gray-100 text-gray-800 rounded-full"
                        >
                          <Tag className="h-3 w-3 mr-1" />
                          {tag}
                        </span>
                      ))}
                    </div>
                  </div>
                )}

                {/* Education & Experience */}
                {(selectedJob.education || selectedJob.experience) && (
                  <div className="pt-4 border-t border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-2">
                      Requirements
                    </h4>
                    {selectedJob.education && (
                      <div className="mb-2">
                        <span className="text-sm font-medium text-gray-700">
                          Education:{" "}
                        </span>
                        <span className="text-sm text-gray-600">
                          {selectedJob.education}
                        </span>
                      </div>
                    )}
                    {selectedJob.experience && (
                      <div>
                        <span className="text-sm font-medium text-gray-700">
                          Experience:{" "}
                        </span>
                        <span className="text-sm text-gray-600">
                          {selectedJob.experience}
                        </span>
                      </div>
                    )}
                  </div>
                )}

                {/* Created Date */}
                <div className="pt-4 border-t border-gray-200">
                  <p className="text-sm text-gray-500">
                    Added: {new Date(selectedJob.created_at).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-sm border p-6 text-center">
              <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">Select a job to view details</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobsTab;
