#!/usr/bin/env python3
# coding: utf-8

"""
Created on Thu Sep 13 2018

Authors:
Thomas Bonald <thomas.bonald@telecom-paristech.fr>
Nathan De Lara <nathan.delara@telecom-paristech.fr>

Spectral embedding by decomposition of the normalized graph Laplacian.
"""

import numpy as np
from scipy import sparse, errstate, sqrt, isinf
from scipy.sparse import csgraph
from scipy.sparse.linalg import eigsh


class SpectralEmbedding:
    """Spectral embedding of a graph

        Attributes
        ----------
        embedding_ : array, shape = (n_nodes, embedding_dimension)
            Embedding matrix of the nodes

        eigenvalues_ : array, shape = (embedding_dimension)
            Smallest eigenvalues of the training matrix

        References
        ----------
        * Laplacian Eigenmaps for Dimensionality Reduction and Data Representation, M. Belkin, P. Niyogi
        """

    def __init__(self, embedding_dimension=10):
        """
        Parameters
        ----------
        embedding_dimension : int, optional
            Dimension of the embedding space (default=10)
        """

        self.embedding_dimension = embedding_dimension
        self.embedding_ = None
        self.eigenvalues_ = None

    def fit(self, adjacency_matrix):
        """Fits the model from data in adjacency_matrix

        Parameters
        ----------
        adjacency_matrix : Scipy csr matrix or numpy ndarray
              Adjacency matrix of the graph
        node_weights : {'uniform', 'degree', array of length n_nodes with positive entries}
              Node weights
        """

        if type(adjacency_matrix) == sparse.csr_matrix:
            adj_matrix = adjacency_matrix
        elif sparse.isspmatrix(adjacency_matrix) or type(adjacency_matrix) == np.ndarray:
            adj_matrix = sparse.csr_matrix(adjacency_matrix)
        else:
            raise TypeError(
                "The argument must be a NumPy array or a SciPy Sparse matrix.")
        n_nodes, m_nodes = adj_matrix.shape
        if n_nodes != m_nodes:
            raise ValueError("The adjacency matrix must be a square matrix.")
        #if csgraph.connected_components(adj_matrix, directed=False)[0] > 1:
            #raise ValueError("The graph must be connected.")
        if (adj_matrix != adj_matrix.maximum(adj_matrix.T)).nnz != 0:
            raise ValueError("The adjacency matrix is not symmetric.")

        # builds standard laplacian
        degrees = adj_matrix.dot(np.ones(n_nodes))
        degree_matrix = sparse.diags(degrees, format='csr')
        laplacian = degree_matrix - adj_matrix

        # applies normalization by node weights 
        with errstate(divide='ignore'):
            degrees_inv_sqrt = 1.0 / sqrt(degrees)
        degrees_inv_sqrt[isinf(degrees_inv_sqrt)] = 0
        weight_matrix = sparse.diags(degrees_inv_sqrt, format='csr')
            
        laplacian = weight_matrix.dot(laplacian.dot(weight_matrix))

        # spectral decomposition
        eigenvalues, eigenvectors = eigsh(laplacian, min(self.embedding_dimension + 1, n_nodes - 1), which='SM')
        self.eigenvalues_ = eigenvalues[1:]
        self.embedding_ = np.array(weight_matrix.dot(eigenvectors[:, 1:]))
        
        return self
